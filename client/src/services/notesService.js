// client/src/services/notesService.js
// SAA-C03 study notes: loaded from /notes/*.json, linked to the Claude question sets through topic tags.
// "Reviewed" marks are kept in localStorage (the aws_saa_c03_ prefix lets cloud.js sync them).

import { CLOUD, fetchData, pushProgress } from './cloud.js';
import { fetchSetIndex, fetchSet, loadProgress as loadSetProgress, isAnswerCorrect } from './claudeSetService.js';

const NOTES_PROGRESS_KEY = 'aws_saa_c03_notes_progress';

let indexPromise = null;
let questionsPromise = null;
const topicCache = new Map();

export function fetchNotesIndex() {
  indexPromise ||= fetchData('notes/index.json').then(res => {
    if (!res.ok) throw new Error(`Failed to load notes index (${res.status})`);
    return res.json();
  });
  indexPromise.catch(() => { indexPromise = null; });
  return indexPromise;
}

export function fetchTopic(slug) {
  if (!topicCache.has(slug)) {
    const p = fetchData(`notes/topics/${encodeURIComponent(slug)}.json`).then(res => {
      if (!res.ok) throw new Error(`Note "${slug}" not found`);
      return res.json();
    });
    p.catch(() => topicCache.delete(slug));
    topicCache.set(slug, p);
  }
  return topicCache.get(slug);
}

// Every Claude-set question, tagged with its set id, so notes can list related questions.
export function fetchAllQuestions() {
  questionsPromise ||= fetchSetIndex().then(async index => {
    const sets = await Promise.all(index.sets.map(s => fetchSet(s.id).then(data => ({ id: s.id, data }))));
    return sets.flatMap(({ id, data }) => (data.questions || []).map(q => ({ ...q, setId: id })));
  });
  questionsPromise.catch(() => { questionsPromise = null; });
  return questionsPromise;
}

// Note slugs whose questionTopics overlap a question's topic tags
export function notesForQuestion(index, question) {
  if (!index || !question?.topics?.length) return [];
  const tags = new Set(question.topics);
  return Object.entries(index.topics)
    .filter(([, t]) => (t.questionTopics || []).some(tag => tags.has(tag)))
    .map(([slug, t]) => ({ slug, ...t }));
}

export function questionsForNote(note, questions) {
  const tags = new Set(note.questionTopics || []);
  return questions.filter(q => (q.topics || []).some(tag => tags.has(tag)));
}

// Attempt status of a question from its set's saved progress: 'ok' | 'bad' | 'none'
export function questionStatus(q, progressBySet) {
  const progress = (progressBySet[q.setId] ||= loadSetProgress(q.setId));
  const att = progress.attempts[q.id];
  if (!att) return 'none';
  return isAnswerCorrect(q, att.selected) ? 'ok' : 'bad';
}

export function scoreQuestions(questions, progressBySet = {}) {
  let attempted = 0;
  let correct = 0;
  for (const q of questions) {
    const s = questionStatus(q, progressBySet);
    if (s === 'none') continue;
    attempted++;
    if (s === 'ok') correct++;
  }
  return {
    total: questions.length,
    attempted,
    correct,
    wrong: attempted - correct,
    accuracy: attempted > 0 ? Math.round((correct / attempted) * 100) : null
  };
}

export function loadNotesProgress() {
  try {
    const raw = localStorage.getItem(NOTES_PROGRESS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return { reviewed: Array.isArray(parsed.reviewed) ? parsed.reviewed : [] };
    }
  } catch (e) {
    console.warn('Error reading notes progress:', e);
  }
  return { reviewed: [] };
}

export function toggleReviewed(slug) {
  const progress = loadNotesProgress();
  const reviewed = progress.reviewed.includes(slug)
    ? progress.reviewed.filter(s => s !== slug)
    : [...progress.reviewed, slug];
  const next = { ...progress, reviewed };
  try {
    localStorage.setItem(NOTES_PROGRESS_KEY, JSON.stringify(next));
  } catch (e) {
    console.error('Failed to save notes progress:', e);
  }
  if (CLOUD) pushProgress(NOTES_PROGRESS_KEY, next);
  return next;
}

export function matchesSearch(slug, topic, query) {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const haystack = [slug, topic.title, topic.summary, ...(topic.keywords || []), ...(topic.questionTopics || [])]
    .join(' ')
    .toLowerCase();
  return q.split(/\s+/).every(word => haystack.includes(word));
}
