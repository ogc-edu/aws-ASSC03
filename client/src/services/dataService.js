// client/src/services/dataService.js
// Client-side JSON database and localStorage service for Amazon S3 Static Hosting and Local usage

const STORAGE_KEY = 'aws_saa_c03_user_progress';

let cachedQuestions = null;
let questionMap = new Map();

// Helper to get questions data URL
function getQuestionsUrl() {
  // Supports relative path for S3 sub-buckets or root hosting
  return './questions.json';
}

// 1. Load all questions from JSON database
export async function initQuestions() {
  if (cachedQuestions) {
    return cachedQuestions;
  }

  try {
    // Attempt 1: Fetch static questions.json
    let res = await fetch(getQuestionsUrl());
    if (!res.ok) {
      // Fallback for different subpath or local server API
      res = await fetch('/questions.json');
      if (!res.ok) {
        res = await fetch('/api/questions');
      }
    }
    const data = await res.json();
    cachedQuestions = Array.isArray(data) ? data : (data.questions || []);
    questionMap = new Map(cachedQuestions.map(q => [q.id, q]));
    return cachedQuestions;
  } catch (err) {
    console.error('Failed to load questions.json database:', err);
    throw err;
  }
}

// 2. Progress Storage with localStorage and automatic server migration
export async function initProgress() {
  let localData = null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      localData = JSON.parse(raw);
    }
  } catch (e) {
    console.warn('Error reading localStorage:', e);
  }

  // If localStorage already has attempts or highlights, use it!
  const hasLocalAttempts = localData && Object.keys(localData.attempts || {}).length > 0;
  const hasLocalHighlights = localData && (localData.highlights || []).length > 0;

  if (hasLocalAttempts || hasLocalHighlights) {
    return {
      lastLeftOff: localData.lastLeftOff || 1,
      highlights: Array.isArray(localData.highlights) ? localData.highlights : [],
      attempts: localData.attempts || {}
    };
  }

  // First time or empty localStorage: import all existing progress from server or user_progress.json!
  try {
    let res = await fetch('/api/progress');
    if (!res.ok) {
      res = await fetch('./user_progress.json');
    }
    if (res.ok) {
      const serverData = await res.json();
      if (serverData && (serverData.attempts || serverData.highlights)) {
        const imported = {
          lastLeftOff: serverData.lastLeftOff || 100,
          highlights: Array.isArray(serverData.highlights) ? serverData.highlights : [],
          attempts: serverData.attempts || {}
        };
        // Save to localStorage immediately
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(imported));
        } catch (err) {}
        return imported;
      }
    }
  } catch (e) {
    console.log('No remote progress to import:', e);
  }

  return {
    lastLeftOff: 1,
    highlights: [],
    attempts: {}
  };
}

export function getLocalProgress() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        lastLeftOff: parsed.lastLeftOff || 1,
        highlights: Array.isArray(parsed.highlights) ? parsed.highlights : [],
        attempts: parsed.attempts || {}
      };
    }
  } catch (e) {
    console.warn('Error reading from localStorage:', e);
  }

  return {
    lastLeftOff: 1,
    highlights: [],
    attempts: {}
  };
}

export function saveLocalProgress(progress) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch (e) {
    console.error('Failed to save progress to localStorage:', e);
  }

  // Optional background sync to Express backend if available
  try {
    fetch('/api/progress/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(progress)
    }).catch(() => {});
  } catch (e) {
    // Ignore when offline or on S3
  }
}

// 3. Calculate statistics dynamically checking against authoritative answer keys
export function computeStats(progress, totalCount = 684) {
  const attemptsEntries = Object.entries(progress.attempts || {});
  const totalAttempted = attemptsEntries.length;
  let totalCorrect = 0;

  for (const [qid, att] of attemptsEntries) {
    const q = questionMap.get(Number(qid));
    if (q && q.correctAnswers) {
      const normUser = [...(att.selected || [])].map(s => s.trim().toUpperCase()).sort();
      const normCorrect = [...q.correctAnswers].map(s => s.trim().toUpperCase()).sort();
      if (normUser.length === normCorrect.length && normUser.every((v, i) => v === normCorrect[i])) {
        totalCorrect++;
        continue;
      }
    } else if (att.isCorrect) {
      totalCorrect++;
    }
  }

  const totalIncorrect = totalAttempted - totalCorrect;
  const accuracy = totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) : 0;
  const highlightCount = (progress.highlights || []).length;

  return {
    totalQuestions: totalCount,
    totalAttempted,
    totalCorrect,
    totalIncorrect,
    accuracy,
    highlightCount
  };
}

// 4. Build Question Matrix for Grid modal
export function buildMatrix(questions, progress) {
  const attempts = progress.attempts || {};
  const highlightsSet = new Set(progress.highlights || []);

  return questions.map(q => {
    const att = attempts[q.id];
    let status = 'unattempted';
    if (att) {
      const normUser = [...(att.selected || [])].map(s => s.trim().toUpperCase()).sort();
      const normCorrect = [...(q.correctAnswers || [])].map(s => s.trim().toUpperCase()).sort();
      const isCorrect = normUser.length === normCorrect.length &&
        normUser.every((val, idx) => val === normCorrect[idx]);
      status = isCorrect ? 'correct' : 'incorrect';
    }
    return {
      id: q.id,
      isMulti: q.isMulti || (q.correctAnswers && q.correctAnswers.length > 1),
      isHighlighted: highlightsSet.has(q.id),
      status
    };
  });
}

// 5. Get Single Question hydrated with current user attempt & highlight
export function getHydratedQuestion(id, progress) {
  const base = questionMap.get(Number(id));
  if (!base) return null;

  const isHighlighted = (progress.highlights || []).includes(base.id);
  const rawAttempt = (progress.attempts || {})[base.id] || null;
  let attempt = rawAttempt;

  if (rawAttempt && base.correctAnswers) {
    const normUser = [...(rawAttempt.selected || [])].map(s => s.trim().toUpperCase()).sort();
    const normCorrect = [...base.correctAnswers].map(s => s.trim().toUpperCase()).sort();
    const isCorrect = normUser.length === normCorrect.length &&
      normUser.every((val, idx) => val === normCorrect[idx]);
    attempt = {
      ...rawAttempt,
      isCorrect
    };
  }

  return {
    ...base,
    isHighlighted,
    attempt
  };
}

// 6. Record Attempt
export function recordAttempt(qId, selectedAnswers, progress) {
  const q = questionMap.get(Number(qId));
  if (!q) throw new Error(`Question ${qId} not found`);

  const normUser = [...selectedAnswers].map(s => s.trim().toUpperCase()).sort();
  const normCorrect = [...q.correctAnswers].map(s => s.trim().toUpperCase()).sort();
  const isCorrect = normUser.length === normCorrect.length &&
    normUser.every((val, idx) => val === normCorrect[idx]);

  const updatedAttempts = {
    ...progress.attempts,
    [qId]: {
      selected: selectedAnswers,
      isCorrect,
      timestamp: new Date().toISOString()
    }
  };

  const updatedProgress = {
    ...progress,
    lastLeftOff: qId,
    attempts: updatedAttempts
  };

  saveLocalProgress(updatedProgress);

  const stats = computeStats(updatedProgress, cachedQuestions?.length || 684);

  return {
    isCorrect,
    selected: selectedAnswers,
    progress: updatedProgress,
    stats
  };
}

// 7. Toggle Highlight
export function toggleHighlight(qId, progress) {
  const idNum = Number(qId);
  const currentHighlights = progress.highlights || [];
  let nextHighlights;
  let isHighlighted;

  if (currentHighlights.includes(idNum)) {
    nextHighlights = currentHighlights.filter(id => id !== idNum);
    isHighlighted = false;
  } else {
    nextHighlights = [...currentHighlights, idNum].sort((a, b) => a - b);
    isHighlighted = true;
  }

  const updatedProgress = {
    ...progress,
    highlights: nextHighlights
  };

  saveLocalProgress(updatedProgress);
  const stats = computeStats(updatedProgress, cachedQuestions?.length || 684);

  return {
    isHighlighted,
    highlights: nextHighlights,
    progress: updatedProgress,
    stats
  };
}

// 8. Save Left-Off Question
export function saveLeftOff(qId, progress) {
  const updatedProgress = {
    ...progress,
    lastLeftOff: Number(qId)
  };
  saveLocalProgress(updatedProgress);
  return updatedProgress;
}

// 9. Reset Progress
export function resetLocalProgress(type, questionId, progress) {
  let updatedProgress = { ...progress };

  if (type === 'question' && questionId) {
    const nextAttempts = { ...updatedProgress.attempts };
    delete nextAttempts[questionId];
    updatedProgress.attempts = nextAttempts;
  } else if (type === 'incorrect') {
    const nextAttempts = {};
    for (const [k, v] of Object.entries(updatedProgress.attempts || {})) {
      if (v.isCorrect) {
        nextAttempts[k] = v;
      }
    }
    updatedProgress.attempts = nextAttempts;
  } else if (type === 'attempts') {
    updatedProgress.attempts = {};
  } else if (type === 'highlights') {
    updatedProgress.highlights = [];
  } else if (type === 'all') {
    updatedProgress = {
      lastLeftOff: 1,
      highlights: [],
      attempts: {}
    };
  }

  saveLocalProgress(updatedProgress);
  const stats = computeStats(updatedProgress, cachedQuestions?.length || 684);

  return {
    progress: updatedProgress,
    stats
  };
}
