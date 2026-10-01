import React, { useState } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  CornerDownLeft, 
  Bookmark, 
  CheckCircle, 
  XCircle,
  HelpCircle
} from 'lucide-react';

export default function PaginationBar({
  currentQuestionId,
  totalQuestions,
  onNavigate,
  onPrev,
  onNext,
  canPrev,
  canNext,
  activeFilter,
  onFilterChange,
  highlightCount,
  incorrectCount,
  filteredCount
}) {
  const [jumpInput, setJumpInput] = useState('');

  const handleJumpSubmit = (e) => {
    e.preventDefault();
    const target = parseInt(jumpInput);
    if (target && target >= 1 && target <= totalQuestions) {
      onNavigate(target);
      setJumpInput('');
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 space-y-4">
      
      {/* Filter Chips Bar */}
      <div className="flex items-center justify-between flex-wrap gap-2 pb-3 border-b border-slate-100">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Practice Mode
        </span>
        <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
          <button
            onClick={() => onFilterChange('all')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
              activeFilter === 'all'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All ({totalQuestions})
          </button>

          <button
            onClick={() => onFilterChange('highlighted')}
            className={`flex items-center space-x-1 px-3 py-1 rounded-lg text-xs font-medium transition ${
              activeFilter === 'highlighted'
                ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>Highlighted ({highlightCount})</span>
          </button>

          <button
            onClick={() => onFilterChange('incorrect')}
            className={`flex items-center space-x-1 px-3 py-1 rounded-lg text-xs font-medium transition ${
              activeFilter === 'incorrect'
                ? 'bg-rose-500 text-white font-bold shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Missed ({incorrectCount})</span>
          </button>

          <button
            onClick={() => onFilterChange('unattempted')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
              activeFilter === 'unattempted'
                ? 'bg-blue-600 text-white font-bold shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Unattempted
          </button>
        </div>
      </div>

      {/* Main Navigation Row */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        
        {/* Previous Button */}
        <button
          onClick={onPrev}
          disabled={!canPrev}
          className={`flex items-center space-x-1 px-4 py-2 rounded-xl text-sm font-semibold transition ${
            canPrev
              ? 'bg-slate-100 text-slate-800 hover:bg-slate-200 cursor-pointer'
              : 'bg-slate-50 text-slate-300 cursor-not-allowed border border-slate-100'
          }`}
          title="Previous question (or Left Arrow)"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous</span>
        </button>

        {/* Center: Jump to question input & indicator */}
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-slate-500 hidden sm:inline">
            Question
          </span>
          <form onSubmit={handleJumpSubmit} className="flex items-center space-x-1.5">
            <input
              type="number"
              min={1}
              max={totalQuestions}
              placeholder={String(currentQuestionId)}
              value={jumpInput}
              onChange={(e) => setJumpInput(e.target.value)}
              className="w-16 px-2.5 py-1.5 text-center text-sm font-bold bg-slate-50 border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-amber-500 focus:bg-white text-slate-900"
            />
            <span className="text-sm text-slate-400 font-medium">/ {totalQuestions}</span>
            <button
              type="submit"
              className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-medium transition shadow-xs"
              title="Jump to this question number"
            >
              Go
            </button>
          </form>
        </div>

        {/* Next Button */}
        <button
          onClick={onNext}
          disabled={!canNext}
          className={`flex items-center space-x-1 px-5 py-2 rounded-xl text-sm font-semibold transition ${
            canNext
              ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 cursor-pointer shadow-sm shadow-amber-500/20'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          }`}
          title="Next question (or Right Arrow)"
        >
          <span>Next</span>
          <ChevronRight className="w-4 h-4" />
        </button>

      </div>

      {/* Keyboard Shortcuts Hint */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-100">
        <span className="hidden sm:inline">
          ⌨️ Shortcuts: <kbd className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600 border font-mono">1-4</kbd> to select option, <kbd className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600 border font-mono">←</kbd> / <kbd className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600 border font-mono">→</kbd> to navigate, <kbd className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600 border font-mono">H</kbd> to highlight
        </span>
        {activeFilter !== 'all' && (
          <span className="text-amber-600 font-medium">
            Filtered view: {filteredCount} questions
          </span>
        )}
      </div>

    </div>
  );
}
