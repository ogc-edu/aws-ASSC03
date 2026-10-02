import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Header from './components/Header.jsx';
import QuestionCard from './components/QuestionCard.jsx';
import PaginationBar from './components/PaginationBar.jsx';
import QuestionGridModal from './components/QuestionGridModal.jsx';
import HighlightsModal from './components/HighlightsModal.jsx';
import ResetConfirmModal from './components/ResetConfirmModal.jsx';
import {
  initQuestions,
  getLocalProgress,
  computeStats,
  buildMatrix,
  getHydratedQuestion,
  recordAttempt,
  toggleHighlight,
  saveLeftOff,
  resetLocalProgress
} from './services/dataService.js';

export default function App() {
  const [currentId, setCurrentId] = useState(1);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [progress, setProgress] = useState({
    lastLeftOff: 1,
    highlights: [],
    attempts: {}
  });
  const [stats, setStats] = useState({
    totalQuestions: 684,
    totalAttempted: 0,
    totalCorrect: 0,
    totalIncorrect: 0,
    accuracy: 0,
    highlightCount: 0
  });
  const [matrix, setMatrix] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filter mode: 'all' | 'highlighted' | 'incorrect' | 'unattempted'
  const [activeFilter, setActiveFilter] = useState('all');

  // Modals
  const [isGridOpen, setIsGridOpen] = useState(false);
  const [isHighlightsOpen, setIsHighlightsOpen] = useState(false);
  const [isResetOpen, setIsResetOpen] = useState(false);

  // Load question by ID
  const loadQuestion = useCallback((id, curProgress = progress) => {
    try {
      const q = getHydratedQuestion(id, curProgress);
      if (q) {
        setCurrentQuestion(q);
        setCurrentId(id);
        const updated = saveLeftOff(id, curProgress);
        setProgress(updated);
      }
    } catch (err) {
      console.error(`Error loading question ${id}:`, err);
    }
  }, [progress]);

  // Load questions and initialize on mount
  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        const qs = await initQuestions();
        const initialProgress = getLocalProgress();
        const initialStats = computeStats(initialProgress, qs.length);
        const initialMatrix = buildMatrix(qs, initialProgress);

        setProgress(initialProgress);
        setStats(initialStats);
        setMatrix(initialMatrix);

        // Resume where user left off
        const resumeId = initialProgress.lastLeftOff || 1;
        const initialQ = getHydratedQuestion(resumeId, initialProgress);
        if (initialQ) {
          setCurrentQuestion(initialQ);
          setCurrentId(resumeId);
        }
      } catch (err) {
        console.error('Initialization error:', err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // Filtered list of question IDs based on current activeFilter
  const filteredQuestionIds = useMemo(() => {
    if (activeFilter === 'all') {
      return matrix.map(m => m.id);
    }
    if (activeFilter === 'highlighted') {
      return matrix.filter(m => m.isHighlighted).map(m => m.id);
    }
    if (activeFilter === 'incorrect') {
      return matrix.filter(m => m.status === 'incorrect').map(m => m.id);
    }
    if (activeFilter === 'unattempted') {
      return matrix.filter(m => m.status === 'unattempted').map(m => m.id);
    }
    return matrix.map(m => m.id);
  }, [matrix, activeFilter]);

  // Current index in filtered list
  const currentFilteredIndex = filteredQuestionIds.indexOf(currentId);
  const canPrev = currentFilteredIndex > 0;
  const canNext = currentFilteredIndex < filteredQuestionIds.length - 1;

  // Navigate to previous question
  const handlePrev = useCallback(() => {
    if (canPrev) {
      const prevId = filteredQuestionIds[currentFilteredIndex - 1];
      loadQuestion(prevId);
    }
  }, [canPrev, filteredQuestionIds, currentFilteredIndex, loadQuestion]);

  // Navigate to next question
  const handleNext = useCallback(() => {
    if (canNext) {
      const nextId = filteredQuestionIds[currentFilteredIndex + 1];
      loadQuestion(nextId);
    }
  }, [canNext, filteredQuestionIds, currentFilteredIndex, loadQuestion]);

  // Handle Answer Attempt
  const handleAttempt = (qId, selectedAnswers) => {
    try {
      const res = recordAttempt(qId, selectedAnswers, progress);

      // Update question state
      setCurrentQuestion(prev => ({
        ...prev,
        attempt: {
          selected: res.selected,
          isCorrect: res.isCorrect,
          timestamp: new Date().toISOString()
        }
      }));

      // Update progress & stats
      setProgress(res.progress);
      setStats(res.stats);

      // Update matrix status
      setMatrix(prev => prev.map(item => {
        if (item.id === qId) {
          return {
            ...item,
            status: res.isCorrect ? 'correct' : 'incorrect'
          };
        }
        return item;
      }));

    } catch (err) {
      console.error('Error submitting attempt:', err);
    }
  };

  // Toggle Highlight
  const handleToggleHighlight = (qId) => {
    try {
      const res = toggleHighlight(qId, progress);

      // Update current question if it matches
      if (currentQuestion && currentQuestion.id === qId) {
        setCurrentQuestion(prev => ({ ...prev, isHighlighted: res.isHighlighted }));
      }

      // Update progress & stats
      setProgress(res.progress);
      setStats(res.stats);

      // Update matrix
      setMatrix(prev => prev.map(item => {
        if (item.id === qId) {
          return { ...item, isHighlighted: res.isHighlighted };
        }
        return item;
      }));
    } catch (err) {
      console.error('Error toggling highlight:', err);
    }
  };

  // Reset Single Question Attempt (Try Again)
  const handleResetQuestion = (qId) => {
    try {
      const res = resetLocalProgress('question', qId, progress);

      setCurrentQuestion(prev => ({ ...prev, attempt: null }));
      setProgress(res.progress);
      setStats(res.stats);
      setMatrix(prev => prev.map(m => m.id === qId ? { ...m, status: 'unattempted' } : m));
    } catch (err) {
      console.error('Error resetting question:', err);
    }
  };

  // Confirm Full Reset
  const handleConfirmReset = async (type) => {
    try {
      const res = resetLocalProgress(type, null, progress);
      setProgress(res.progress);
      setStats(res.stats);

      const qs = await initQuestions();
      setMatrix(buildMatrix(qs, res.progress));
      loadQuestion(1, res.progress);
    } catch (err) {
      console.error('Error resetting progress:', err);
    }
  };

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't trigger if user is focused on an input or textarea
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
        return;
      }

      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        handlePrev();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        handleNext();
      } else if (e.key === 'h' || e.key === 'H') {
        e.preventDefault();
        if (currentQuestion) {
          handleToggleHighlight(currentQuestion.id);
        }
      } else if (!currentQuestion?.attempt && !currentQuestion?.isMulti) {
        // Quick select for single-choice questions (1-5 or a-e)
        const keyMap = {
          '1': 'A', 'a': 'A', 'A': 'A',
          '2': 'B', 'b': 'B', 'B': 'B',
          '3': 'C', 'c': 'C', 'C': 'C',
          '4': 'D', 'd': 'D', 'D': 'D',
          '5': 'E', 'e': 'E', 'E': 'E'
        };
        const opt = keyMap[e.key];
        if (opt && currentQuestion.options && currentQuestion.options[opt]) {
          handleAttempt(currentQuestion.id, [opt]);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentQuestion, handlePrev, handleNext, progress]);

  // List of highlighted questions for the modal
  const highlightedList = useMemo(() => {
    const hlSet = new Set(progress.highlights || []);
    return matrix.filter(m => hlSet.has(m.id)).map(m => {
      const fullQ = getHydratedQuestion(m.id, progress);
      return {
        id: m.id,
        prompt: fullQ?.prompt ? fullQ.prompt.slice(0, 140) + '...' : `Question #${m.id}`,
        isMulti: m.isMulti
      };
    });
  }, [matrix, progress]);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col selection:bg-amber-100">
      
      {/* Top Sticky Header */}
      <Header
        stats={stats}
        progress={progress}
        onOpenGrid={() => setIsGridOpen(true)}
        onOpenHighlights={() => setIsHighlightsOpen(true)}
        onOpenReset={() => setIsResetOpen(true)}
        currentQuestionId={currentId}
        onResumeLeftoff={() => loadQuestion(progress.lastLeftOff || 1)}
        activeFilter={activeFilter}
        setActiveFilter={setActiveFilter}
      />

      {/* Main Study Workspace */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Navigation & Practice Mode Controls */}
        <PaginationBar
          currentQuestionId={currentId}
          totalQuestions={stats.totalQuestions || 684}
          onNavigate={(targetId) => loadQuestion(targetId)}
          onPrev={handlePrev}
          onNext={handleNext}
          canPrev={canPrev}
          canNext={canNext}
          activeFilter={activeFilter}
          onFilterChange={(filter) => {
            setActiveFilter(filter);
            setTimeout(() => {
              const matched = matrix.filter(m => {
                if (filter === 'highlighted') return m.isHighlighted;
                if (filter === 'incorrect') return m.status === 'incorrect';
                if (filter === 'unattempted') return m.status === 'unattempted';
                return true;
              });
              if (matched.length > 0 && !matched.some(m => m.id === currentId)) {
                loadQuestion(matched[0].id);
              }
            }, 50);
          }}
          highlightCount={stats.highlightCount}
          incorrectCount={stats.totalIncorrect}
          filteredCount={filteredQuestionIds.length}
        />

        {/* Question Card */}
        {loading ? (
          <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-amber-500 border-t-transparent" />
            <p className="mt-3 text-slate-500 text-sm font-medium">Loading AWS Question Bank...</p>
          </div>
        ) : (
          <QuestionCard
            question={currentQuestion}
            onAttempt={handleAttempt}
            onToggleHighlight={handleToggleHighlight}
            onResetQuestion={handleResetQuestion}
            onNext={handleNext}
            onPrev={handlePrev}
            isFirst={!canPrev}
            isLast={!canNext}
            isLeftOff={progress.lastLeftOff === currentId}
          />
        )}

      </main>

      {/* Footer */}
      <footer className="py-6 border-t border-slate-200/80 text-center text-xs text-slate-400">
        AWS Certified Solutions Architect – Associate (SAA-C03) Exam Practice System • Static S3 Serverless Engine
      </footer>

      {/* Modals */}
      <QuestionGridModal
        isOpen={isGridOpen}
        onClose={() => setIsGridOpen(false)}
        matrix={matrix}
        currentQuestionId={currentId}
        onSelectQuestion={(id) => loadQuestion(id)}
      />

      <HighlightsModal
        isOpen={isHighlightsOpen}
        onClose={() => setIsHighlightsOpen(false)}
        highlightedQuestions={highlightedList}
        onSelectQuestion={(id) => loadQuestion(id)}
        onRemoveHighlight={(id) => handleToggleHighlight(id)}
        attempts={progress.attempts || {}}
      />

      <ResetConfirmModal
        isOpen={isResetOpen}
        onClose={() => setIsResetOpen(false)}
        onConfirmReset={handleConfirmReset}
      />

    </div>
  );
}
