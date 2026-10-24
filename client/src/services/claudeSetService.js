// client/src/services/claudeSetService.js
// Claude-generated SAA-C03 question sets: loaded from /claude/*.json, progress kept per set in localStorage.
// Kept fully separate from the main question bank (dataService.js) and its progress key.

import { CLOUD, fetchData, pushProgress } from './cloud.js';

const progressKey = (setId) => `aws_saa_c03_claude_set_${setId}_progress`;

const emptyProgress = () => ({ lastLeftOff: 1, highlights: [], attempts: {} });

export async function fetchSetIndex() {
  const res = await fetchData('claude/sets.json');
  if (!res.ok) throw new Error(`Failed to load Claude set index (${res.status})`);
  return res.json();
}

export async function fetchSet(setId) {
  const res = await fetchData(`claude/set-${encodeURIComponent(setId)}.json`);
  if (!res.ok) throw new Error(`Question set "${setId}" not found`);
  return res.json();
}

export function loadProgress(setId) {
  try {
    const raw = localStorage.getItem(progressKey(setId));
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        lastLeftOff: parsed.lastLeftOff || 1,
        highlights: Array.isArray(parsed.highlights) ? parsed.highlights : [],
        attempts: parsed.attempts || {}
      };
    }
  } catch (e) {
    console.warn('Error reading Claude set progress:', e);
  }
  return emptyProgress();
}

export function saveProgress(setId, progress) {
  try {
    localStorage.setItem(progressKey(setId), JSON.stringify(progress));
  } catch (e) {
    console.error('Failed to save Claude set progress:', e);
  }
  if (CLOUD) pushProgress(progressKey(setId), progress);
}

export function clearProgress(setId) {
  const fresh = emptyProgress();
  saveProgress(setId, fresh);
  return fresh;
}

export function isAnswerCorrect(question, selected) {
  const norm = (arr) => [...(arr || [])].map(s => s.trim().toUpperCase()).sort();
  const user = norm(selected);
  const correct = norm(question.correctAnswers);
  return user.length === correct.length && user.every((v, i) => v === correct[i]);
}

// Overall + per-domain score for a set
export function computeSetStats(questions, progress) {
  const attempts = progress.attempts || {};
  const byDomain = {};
  let attempted = 0;
  let correct = 0;

  for (const q of questions) {
    const d = (byDomain[q.domain] ||= { total: 0, attempted: 0, correct: 0 });
    d.total++;
    const att = attempts[q.id];
    if (!att) continue;
    attempted++;
    d.attempted++;
    if (isAnswerCorrect(q, att.selected)) {
      correct++;
      d.correct++;
    }
  }

  return {
    total: questions.length,
    attempted,
    correct,
    incorrect: attempted - correct,
    accuracy: attempted > 0 ? Math.round((correct / attempted) * 100) : 0,
    // Score over the whole set (unanswered = incorrect, as on the real exam)
    examPercent: questions.length > 0 ? Math.round((correct / questions.length) * 100) : 0,
    byDomain
  };
}
