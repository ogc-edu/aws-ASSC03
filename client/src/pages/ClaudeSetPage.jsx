import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { BookOpen, ChevronLeft, ChevronRight, Grid3X3, RotateCcw, Trophy } from 'lucide-react';
import ClaudeHeader from '../components/ClaudeHeader.jsx';
import QuestionCard from '../components/QuestionCard.jsx';
import { fetchNotesIndex, notesForQuestion } from '../services/notesService.js';
import {
  fetchSet,
  loadProgress,
  saveProgress,
  clearProgress,
  isAnswerCorrect,
  computeSetStats
} from '../services/claudeSetService.js';

const DOMAIN_NAMES = {
  1: 'Design Secure Architectures',
  2: 'Design Resilient Architectures',
  3: 'Design High-Performing Architectures',
  4: 'Design Cost-Optimized Architectures'
};

export default function ClaudeSetPage({ setId }) {
  const [set, setSet] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(() => loadProgress(setId));
  // ?q=<id> (links from the notes) opens that question instead of the left-off one
  const [currentId, setCurrentId] = useState(() => {
    const q = parseInt(new URLSearchParams(window.location.search).get('q'), 10);
    if (q > 0) {
      window.history.replaceState({}, '', window.location.pathname);
      return q;
    }
    return loadProgress(setId).lastLeftOff || 1;
  });
  const [showGrid, setShowGrid] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [notesIndex, setNotesIndex] = useState(null);

  useEffect(() => {
    // Notes are optional here: without them the question page just shows no study links.
    fetchNotesIndex().then(setNotesIndex).catch(() => {});
  }, []);

  useEffect(() => {
    fetchSet(setId)
      .then(data => {
        setSet(data);
        document.title = `${data.title} • SAA-C03`;
      })
      .catch(err => setError(err.message));
  }, [setId]);

  const questions = set?.questions || [];
  const total = questions.length;

  const updateProgress = useCallback((next) => {
    setProgress(next);
    saveProgress(setId, next);
  }, [setId]);

  const goTo = useCallback((id) => {
    if (id < 1 || id > total) return;
    setCurrentId(id);
    updateProgress({ ...progress, lastLeftOff: id });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [total, progress, updateProgress]);

  const base = questions.find(q => q.id === currentId) || questions[0];
  const currentQuestion = useMemo(() => {
    if (!base) return null;
    const raw = progress.attempts[base.id];
    return {
      ...base,
      isHighlighted: progress.highlights.includes(base.id),
      attempt: raw ? { ...raw, isCorrect: isAnswerCorrect(base, raw.selected) } : null
    };
  }, [base, progress]);

  const stats = useMemo(() => computeSetStats(questions, progress), [questions, progress]);
  const studyNotes = useMemo(() => notesForQuestion(notesIndex, base), [notesIndex, base]);

  const handleAttempt = (qId, selected) => {
    const q = questions.find(x => x.id === qId);
    updateProgress({
      ...progress,
      lastLeftOff: qId,
      attempts: {
        ...progress.attempts,
        [qId]: { selected, isCorrect: isAnswerCorrect(q, selected), timestamp: new Date().toISOString() }
      }
    });
  };

  const handleToggleHighlight = (qId) => {
    const has = progress.highlights.includes(qId);
    updateProgress({
      ...progress,
      highlights: has ? progress.highlights.filter(h => h !== qId) : [...progress.highlights, qId].sort((a, b) => a - b)
    });
  };

  const handleResetQuestion = (qId) => {
    const nextAttempts = { ...progress.attempts };
    delete nextAttempts[qId];
    updateProgress({ ...progress, attempts: nextAttempts });
  };

  const handleResetSet = () => {
    if (window.confirm('Reset all answers and highlights for this set?')) {
      updateProgress(clearProgress(setId));
      setCurrentId(1);
      setShowResults(false);
    }
  };

  useEffect(() => {
    const onKey = (e) => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
      if (e.key === 'ArrowLeft') goTo(currentId - 1);
      else if (e.key === 'ArrowRight') goTo(currentId + 1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [currentId, goTo]);

  if (error) {
    return (
      <div className="min-h-screen bg-slate-100">
        <ClaudeHeader title="Claude Practice Sets" backHref="/claude" backLabel="All Claude Sets" />
        <div className="max-w-4xl mx-auto p-8">
          <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl p-4 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col selection:bg-amber-100">
      <ClaudeHeader
        title={set ? set.title : 'Loading set...'}
        subtitle={set ? `${total} questions • Claude-generated • mirrors ${set.examCode} blueprint` : ''}
        backHref="/claude"
        backLabel="All Claude Sets"
      >
        <a href="/" className="hidden md:inline-flex items-center px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-slate-400 hover:text-white transition">
          Main Bank
        </a>
        <a href="/notes" className="hidden md:inline-flex items-center px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-teal-300 hover:text-teal-200 transition">
          <BookOpen className="w-4 h-4 mr-1.5" /> Notes
        </a>
      </ClaudeHeader>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {!set ? (
          <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-violet-500 border-t-transparent" />
          </div>
        ) : (
          <>
            {/* Progress + controls */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => goTo(currentId - 1)}
                    disabled={currentId <= 1}
                    className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                    title="Previous (←)"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-sm font-medium text-slate-700 font-mono">
                    {currentId} / {total}
                  </span>
                  <button
                    onClick={() => goTo(currentId + 1)}
                    disabled={currentId >= total}
                    className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                    title="Next (→)"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowGrid(v => !v)}
                    className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium border transition ${showGrid ? 'bg-slate-900 text-white border-slate-900' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'}`}
                  >
                    <Grid3X3 className="w-4 h-4 mr-1.5" /> Matrix
                  </button>
                  <button
                    onClick={() => setShowResults(v => !v)}
                    className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium border transition ${showResults ? 'bg-violet-600 text-white border-violet-600' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'}`}
                  >
                    <Trophy className="w-4 h-4 mr-1.5" /> Score
                  </button>
                  <button
                    onClick={handleResetSet}
                    className="p-2 text-slate-400 hover:text-rose-500 hover:bg-slate-50 rounded-lg transition"
                    title="Reset this set"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="flex justify-between text-xs text-slate-500">
                <span>Attempted {stats.attempted}/{total}</span>
                <span>Accuracy {stats.accuracy}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden flex">
                <div className="bg-emerald-500 h-full" style={{ width: `${(stats.correct / total) * 100}%` }} />
                <div className="bg-rose-500 h-full" style={{ width: `${(stats.incorrect / total) * 100}%` }} />
              </div>

              {showGrid && (
                <div className="grid gap-1.5 pt-2" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(2.25rem, 1fr))' }}>
                  {questions.map(q => {
                    const att = progress.attempts[q.id];
                    const status = !att ? 'none' : isAnswerCorrect(q, att.selected) ? 'ok' : 'bad';
                    const cls = status === 'ok'
                      ? 'bg-emerald-500 text-white border-emerald-500'
                      : status === 'bad'
                        ? 'bg-rose-500 text-white border-rose-500'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-violet-400';
                    return (
                      <button
                        key={q.id}
                        onClick={() => goTo(q.id)}
                        title={`Q${q.id} • Domain ${q.domain}${q.isMulti ? ' • multiple response' : ''}`}
                        className={`relative h-9 rounded-md border text-xs font-mono font-semibold transition ${cls} ${q.id === currentId ? 'ring-2 ring-violet-500 ring-offset-1' : ''}`}
                      >
                        {q.id}
                        {progress.highlights.includes(q.id) && (
                          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-amber-400 border border-white" />
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {showResults && <ResultsPanel stats={stats} passingPercent={set.format?.approxPassingPercent ?? 72} />}

            {/* Domain / task context for the current question */}
            {currentQuestion && (
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="px-2.5 py-1 rounded-md bg-violet-50 text-violet-800 border border-violet-200 font-semibold">
                  Domain {currentQuestion.domain}: {DOMAIN_NAMES[currentQuestion.domain]}
                </span>
                {currentQuestion.task && (
                  <span className="px-2.5 py-1 rounded-md bg-slate-200/70 text-slate-700 font-medium">Task {currentQuestion.task}</span>
                )}
                {currentQuestion.attempt && (currentQuestion.topics || []).map(t => (
                  <span key={t} className="px-2 py-1 rounded-md bg-white text-slate-500 border border-slate-200">{t}</span>
                ))}
              </div>
            )}

            {currentQuestion?.attempt && studyNotes.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 bg-teal-50 border border-teal-200 rounded-xl px-4 py-3">
                <span className="text-sm font-semibold text-teal-900 mr-1">Study this topic:</span>
                {studyNotes.map(n => (
                  <a
                    key={n.slug}
                    href={`/notes/${n.slug}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-white border border-teal-300 text-teal-900 hover:bg-teal-600 hover:border-teal-600 hover:text-white transition"
                  >
                    <BookOpen className="w-4 h-4" /> {n.title}
                  </a>
                ))}
              </div>
            )}

            <QuestionCard
              question={currentQuestion}
              onAttempt={handleAttempt}
              onToggleHighlight={handleToggleHighlight}
              onResetQuestion={handleResetQuestion}
              onNext={() => goTo(currentId + 1)}
              onPrev={() => goTo(currentId - 1)}
              isFirst={currentId <= 1}
              isLast={currentId >= total}
              isLeftOff={false}
            />
          </>
        )}
      </main>

      <footer className="py-6 border-t border-slate-200/80 text-center text-xs text-slate-400">
        Claude-generated practice set • Not official AWS exam content
      </footer>
    </div>
  );
}

function ResultsPanel({ stats, passingPercent }) {
  const passed = stats.examPercent >= passingPercent;
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-xs text-slate-500">Score over all {stats.total} questions (unanswered count as wrong)</div>
          <div className="text-3xl font-bold text-slate-900">
            {stats.correct}/{stats.total} <span className="text-lg text-slate-500">({stats.examPercent}%)</span>
          </div>
        </div>
        <span className={`px-3 py-1.5 rounded-lg text-sm font-semibold border ${passed ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-amber-50 text-amber-800 border-amber-200'}`}>
          {passed ? 'On track to pass' : 'Below target'} (target ≈ {passingPercent}%)
        </span>
      </div>
      <div className="space-y-2">
        {Object.entries(stats.byDomain).sort(([a], [b]) => a - b).map(([d, s]) => {
          const pct = s.total ? Math.round((s.correct / s.total) * 100) : 0;
          return (
            <div key={d} className="flex items-center gap-3 text-sm">
              <span className="w-56 sm:w-72 text-slate-700 truncate">D{d}: {DOMAIN_NAMES[d]}</span>
              <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-violet-500" style={{ width: `${pct}%` }} />
              </div>
              <span className="w-20 text-right font-mono text-xs text-slate-600">{s.correct}/{s.total}</span>
            </div>
          );
        })}
      </div>
      <p className="text-[11px] text-slate-400">
        The real exam reports a scaled score (100–1,000, pass 720), not a raw percentage; the target here is an approximation.
      </p>
    </div>
  );
}
