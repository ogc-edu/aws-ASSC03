const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5001;

app.use(cors());
app.use(express.json());

const { execFile } = require('child_process');

const QUESTIONS_PATH = path.join(__dirname, 'data', 'questions.json');
const PROGRESS_PATH = path.join(__dirname, 'data', 'user_progress.json');
const DETAILED_CACHE_PATH = path.join(__dirname, 'data', 'detailed_explanations.json');
const AGY_BIN = '/Users/ooiguancheng/.local/bin/agy';

// Load questions
let questions = [];
try {
  const qData = fs.readFileSync(QUESTIONS_PATH, 'utf-8');
  questions = JSON.parse(qData);
  console.log(`Loaded ${questions.length} questions from data/questions.json`);
} catch (err) {
  console.error('Failed to load questions.json:', err.message);
}

// Map for quick ID lookup
const questionMap = new Map(questions.map(q => [q.id, q]));

// Load or initialize user progress
function getProgress() {
  if (fs.existsSync(PROGRESS_PATH)) {
    try {
      const data = fs.readFileSync(PROGRESS_PATH, 'utf-8');
      return JSON.parse(data);
    } catch (e) {
      console.error('Error reading progress file, re-initializing:', e.message);
    }
  }
  const initial = {
    lastLeftOff: 1,
    highlights: [],
    attempts: {}
  };
  saveProgress(initial);
  return initial;
}

function saveProgress(progress) {
  try {
    fs.writeFileSync(PROGRESS_PATH, JSON.stringify(progress, null, 2), 'utf-8');
  } catch (err) {
    console.error('Failed to save progress:', err.message);
  }
}

// Compute statistics helper
function calculateStats(progress) {
  const attempts = progress.attempts || {};
  const totalAttempted = Object.keys(attempts).length;
  let totalCorrect = 0;
  let totalIncorrect = 0;

  for (const qId in attempts) {
    if (attempts[qId].isCorrect) {
      totalCorrect++;
    } else {
      totalIncorrect++;
    }
  }

  const accuracy = totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) : 0;
  return {
    totalQuestions: questions.length,
    totalAttempted,
    totalCorrect,
    totalIncorrect,
    accuracy,
    highlightCount: (progress.highlights || []).length
  };
}

// API Routes

// 1. Get Questions (Paginated or filtered)
app.get('/api/questions', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 20;
  const filter = req.query.filter || 'all'; // all, highlighted, correct, incorrect, unattempted
  const search = (req.query.search || '').trim().toLowerCase();

  const progress = getProgress();
  const highlightsSet = new Set(progress.highlights || []);
  const attempts = progress.attempts || {};

  let filtered = questions.filter(q => {
    // Filter by search text
    if (search) {
      const promptMatch = q.prompt.toLowerCase().includes(search);
      const optMatch = Object.values(q.options).some(o => o.toLowerCase().includes(search));
      const idMatch = String(q.id).includes(search);
      if (!promptMatch && !optMatch && !idMatch) return false;
    }

    // Filter by type
    if (filter === 'highlighted') {
      return highlightsSet.has(q.id);
    }
    if (filter === 'attempted') {
      return !!attempts[q.id];
    }
    if (filter === 'unattempted') {
      return !attempts[q.id];
    }
    if (filter === 'correct') {
      return attempts[q.id] && attempts[q.id].isCorrect;
    }
    if (filter === 'incorrect') {
      return attempts[q.id] && !attempts[q.id].isCorrect;
    }

    return true;
  });

  const total = filtered.length;
  const totalPages = Math.ceil(total / limit) || 1;
  const startIndex = (page - 1) * limit;
  const paginated = filtered.slice(startIndex, startIndex + limit);

  // Attach quick state to each item
  const result = paginated.map(q => ({
    id: q.id,
    prompt: q.prompt,
    options: q.options,
    isMulti: q.isMulti,
    requiredCount: q.requiredCount,
    correctAnswers: q.correctAnswers,
    explanation: q.explanation,
    isHighlighted: highlightsSet.has(q.id),
    attempt: attempts[q.id] || null
  }));

  res.json({
    total,
    page,
    limit,
    totalPages,
    questions: result
  });
});

// 2. Get Single Question by ID
app.get('/api/questions/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const q = questionMap.get(id);
  if (!q) {
    return res.status(404).json({ error: 'Question not found' });
  }

  const progress = getProgress();
  const isHighlighted = (progress.highlights || []).includes(id);
  const attempt = (progress.attempts || {})[id] || null;

  res.json({
    ...q,
    isHighlighted,
    attempt
  });
});

// 3. Get Overview Matrix / IDs list with statuses
app.get('/api/questions-matrix', (req, res) => {
  const progress = getProgress();
  const highlightsSet = new Set(progress.highlights || []);
  const attempts = progress.attempts || {};

  const matrix = questions.map(q => {
    const att = attempts[q.id];
    let status = 'unattempted';
    if (att) {
      status = att.isCorrect ? 'correct' : 'incorrect';
    }
    return {
      id: q.id,
      status,
      isHighlighted: highlightsSet.has(q.id),
      isMulti: q.isMulti
    };
  });

  res.json(matrix);
});

// 3b. Generate or fetch deep independent option-by-option AI explanation
app.post('/api/questions/:id/ai-explain', (req, res) => {
  const id = parseInt(req.params.id);
  const q = questionMap.get(id);
  if (!q) {
    return res.status(404).json({ error: 'Question not found' });
  }

  // Check cache first
  let cache = {};
  if (fs.existsSync(DETAILED_CACHE_PATH)) {
    try {
      cache = JSON.parse(fs.readFileSync(DETAILED_CACHE_PATH, 'utf-8'));
    } catch (e) {}
  }

  if (cache[String(id)] && cache[String(id)].includes('Why Other Options Are Incorrect')) {
    return res.json({ id, explanation: cache[String(id)], cached: true });
  }

  // Generate on the fly
  const correctStr = (q.correctAnswers || []).join(', ');
  const optionsText = Object.entries(q.options || {})
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k}: ${v}`)
    .join('\n');

  const userPrompt = `You are an elite AWS Solutions Architect Associate (SAA-C03) instructor.
Review this exact exam question and provide a rigorous, independent technical evaluation for EACH option.

STRICT INSTRUCTIONS:
- EVERY OPTION MUST BE VALUED AND EXPLAINED INDEPENDENTLY WITH CONCRETE TECHNICAL REASONS.
- NEVER USE GENERIC PHRASES LIKE "this answer is not effective", "does not meet requirements", or "introduces suboptimal trade-offs".
- Clearly explain the exact technical mechanism: why the correct option works and why EVERY OTHER option is technically wrong (e.g. wrong protocol, lacks durability, excessive operational complexity, incompatible API, unsupported feature, high latency, missing requirement, etc.).

Question:
${q.prompt}

Options:
${optionsText}

Correct Answer: Option ${correctStr}

Format your output in clean Markdown with these exact sections:
### ✅ Why Option ${correctStr} is Correct
(Provide concrete technical explanation detailing the AWS service features, architecture pattern, and how it satisfies the scenario)

---

### ❌ Why Other Options Are Incorrect
(For EVERY single incorrect option letter, provide a dedicated bullet explaining the specific technical flaw)

---

### 💡 SAA-C03 Exam Concept & AWS Best Practice
(2-3 key takeaways and architecture rules of thumb tested by this question)`;

  execFile(AGY_BIN, ['--model', 'gemini-3.8-flash-low', '-p', userPrompt], { timeout: 45000 }, (error, stdout, stderr) => {
    if (error || !stdout.trim()) {
      console.error(`AI generation failed for Q${id}:`, error?.message || stderr);
      return res.status(500).json({ error: 'Failed to generate explanation', details: error?.message });
    }

    const explanation = stdout.trim();
    // Cache to detailed_explanations.json
    cache[String(id)] = explanation;
    try {
      fs.writeFileSync(DETAILED_CACHE_PATH, JSON.stringify(cache, null, 2), 'utf-8');
      // Also update question in memory and questions.json
      q.explanation = explanation;
      fs.writeFileSync(QUESTIONS_PATH, JSON.stringify(questions, null, 2), 'utf-8');
    } catch (e) {
      console.error('Failed to write explanation cache:', e.message);
    }

    res.json({ id, explanation, cached: false });
  });
});

// 4. Get User Progress & Stats
app.get('/api/progress', (req, res) => {
  const progress = getProgress();
  const stats = calculateStats(progress);
  res.json({
    lastLeftOff: progress.lastLeftOff || 1,
    highlights: progress.highlights || [],
    attempts: progress.attempts || {},
    stats
  });
});

// 5. Update Leftoff Question
app.post('/api/progress/leftoff', (req, res) => {
  const { questionId } = req.body;
  const id = parseInt(questionId);
  if (!id || !questionMap.has(id)) {
    return res.status(400).json({ error: 'Invalid questionId' });
  }

  const progress = getProgress();
  progress.lastLeftOff = id;
  saveProgress(progress);

  res.json({ success: true, lastLeftOff: id });
});

// 6. Toggle Highlight
app.post('/api/progress/highlight', (req, res) => {
  const { questionId } = req.body;
  const id = parseInt(questionId);
  if (!id || !questionMap.has(id)) {
    return res.status(400).json({ error: 'Invalid questionId' });
  }

  const progress = getProgress();
  if (!progress.highlights) progress.highlights = [];

  const index = progress.highlights.indexOf(id);
  let isHighlighted = false;
  if (index >= 0) {
    progress.highlights.splice(index, 1);
    isHighlighted = false;
  } else {
    progress.highlights.push(id);
    progress.highlights.sort((a, b) => a - b);
    isHighlighted = true;
  }

  saveProgress(progress);
  res.json({ success: true, questionId: id, isHighlighted, highlights: progress.highlights });
});

// 7. Record Question Attempt
app.post('/api/progress/attempt', (req, res) => {
  const { questionId, selectedAnswers } = req.body;
  const id = parseInt(questionId);
  const q = questionMap.get(id);

  if (!q) {
    return res.status(404).json({ error: 'Question not found' });
  }

  if (!Array.isArray(selectedAnswers)) {
    return res.status(400).json({ error: 'selectedAnswers must be an array of option letters' });
  }

  const sortedSelected = [...selectedAnswers].map(s => String(s).toUpperCase()).sort();
  const sortedCorrect = [...q.correctAnswers].map(c => String(c).toUpperCase()).sort();

  // Evaluate correctness:
  // For single select: matches
  // For multi select: both sorted arrays must match exactly
  const isCorrect = sortedSelected.length === sortedCorrect.length &&
    sortedSelected.every((val, idx) => val === sortedCorrect[idx]);

  const progress = getProgress();
  if (!progress.attempts) progress.attempts = {};

  progress.attempts[id] = {
    selected: sortedSelected,
    isCorrect,
    timestamp: new Date().toISOString()
  };
  // Automatically update lastLeftOff
  progress.lastLeftOff = id;

  saveProgress(progress);

  res.json({
    questionId: id,
    selected: sortedSelected,
    isCorrect,
    correctAnswers: q.correctAnswers,
    explanation: q.explanation,
    stats: calculateStats(progress)
  });
});

// 8. Reset Progress
app.post('/api/progress/reset', (req, res) => {
  const { type, questionId } = req.body; // 'all', 'question', 'attempts-only'
  const progress = getProgress();

  if (type === 'question' && questionId) {
    delete progress.attempts[questionId];
  } else if (type === 'attempts-only') {
    progress.attempts = {};
  } else {
    progress.lastLeftOff = 1;
    progress.highlights = [];
    progress.attempts = {};
  }

  saveProgress(progress);
  res.json({ success: true, progress, stats: calculateStats(progress) });
});

// 9. Sync full progress from client (localStorage sync)
app.post('/api/progress/sync', (req, res) => {
  const incoming = req.body;
  if (!incoming) return res.status(400).json({ error: 'No data' });
  const current = getProgress();
  const merged = {
    lastLeftOff: incoming.lastLeftOff || current.lastLeftOff || 1,
    highlights: Array.isArray(incoming.highlights) ? incoming.highlights : (current.highlights || []),
    attempts: { ...(current.attempts || {}), ...(incoming.attempts || {}) }
  };
  saveProgress(merged);
  res.json({ success: true, progress: merged, stats: calculateStats(merged) });
});

// Serve client static files if built
const clientDistPath = path.join(__dirname, '..', 'client', 'dist');
if (fs.existsSync(clientDistPath)) {
  app.use(express.static(clientDistPath));
  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/api')) {
      return next();
    }
    res.sendFile(path.join(clientDistPath, 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`\n==================================================`);
  console.log(`🚀 AWS SAA-C03 Practice Website is running!`);
  console.log(`🌐 Local URL: http://localhost:${PORT}`);
  console.log(`==================================================\n`);
});
