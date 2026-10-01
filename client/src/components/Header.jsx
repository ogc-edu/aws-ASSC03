import React from 'react';
import { 
  Bookmark, 
  Grid3X3, 
  RotateCcw, 
  Award, 
  CheckCircle2, 
  XCircle, 
  Layers, 
  HelpCircle,
  ExternalLink
} from 'lucide-react';

export default function Header({ 
  stats, 
  progress, 
  onOpenGrid, 
  onOpenHighlights, 
  onOpenReset, 
  currentQuestionId,
  onResumeLeftoff,
  activeFilter,
  setActiveFilter
}) {
  const lastLeftOff = progress?.lastLeftOff || 1;
  const highlightCount = progress?.highlights?.length || 0;
  const totalAttempted = stats?.totalAttempted || 0;
  const totalQuestions = stats?.totalQuestions || 684;
  const totalCorrect = stats?.totalCorrect || 0;
  const accuracy = stats?.accuracy || 0;
  const percentComplete = Math.round((totalAttempted / totalQuestions) * 100);

  return (
    <header className="sticky top-0 z-30 bg-slate-900 border-b border-slate-800 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Exam Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-400 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <span className="font-extrabold text-slate-950 text-xl tracking-tight">AWS</span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="font-bold text-base sm:text-lg text-slate-100 leading-tight">
                  SAA-C03 Practice Hub
                </h1>
                <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Associate 2026
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                684 Solved Questions & Comprehensive Architecture Solutions
              </p>
            </div>
          </div>

          {/* Center Progress Bar (Desktop) */}
          <div className="hidden lg:flex items-center space-x-6 flex-1 max-w-md mx-8">
            <div className="w-full">
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>Progress: {totalAttempted} / {totalQuestions} ({percentComplete}%)</span>
                <span>Accuracy: {accuracy}%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden flex">
                <div 
                  className="bg-emerald-500 h-full transition-all duration-300"
                  style={{ width: `${(totalCorrect / totalQuestions) * 100}%` }}
                  title={`Correct: ${totalCorrect}`}
                />
                <div 
                  className="bg-rose-500 h-full transition-all duration-300"
                  style={{ width: `${((totalAttempted - totalCorrect) / totalQuestions) * 100}%` }}
                  title={`Incorrect: ${totalAttempted - totalCorrect}`}
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* Resume Leftoff button if currently not on it */}
            {currentQuestionId !== lastLeftOff && (
              <button
                onClick={onResumeLeftoff}
                className="hidden sm:inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500 hover:bg-amber-400 text-slate-950 transition shadow-sm"
                title={`Jump to Question #${lastLeftOff}`}
              >
                Resume Q#{lastLeftOff}
              </button>
            )}

            {/* Highlights Section Button */}
            <button
              onClick={onOpenHighlights}
              className={`relative inline-flex items-center px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium border transition ${
                highlightCount > 0 
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/20' 
                  : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Bookmark className="w-4 h-4 mr-1.5 text-amber-400 fill-amber-400/20" />
              <span>Highlights</span>
              {highlightCount > 0 && (
                <span className="ml-1.5 px-1.5 py-0.2 bg-amber-500 text-slate-950 text-xs font-bold rounded-full">
                  {highlightCount}
                </span>
              )}
            </button>

            {/* Grid / Matrix Overview */}
            <button
              onClick={onOpenGrid}
              className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition"
              title="View all 684 questions in matrix grid"
            >
              <Grid3X3 className="w-4 h-4 mr-1.5 text-blue-400" />
              <span className="hidden sm:inline">Question</span> Matrix
            </button>

            {/* Reset Progress */}
            <button
              onClick={onOpenReset}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
              title="Reset progress"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Progress Bar */}
      <div className="lg:hidden px-4 pb-2 pt-1 border-t border-slate-800/60 bg-slate-900/60 flex items-center justify-between text-xs text-slate-300">
        <div>
          Attempted: <span className="font-semibold text-white">{totalAttempted}</span> / {totalQuestions}
        </div>
        <div>
          Accuracy: <span className="font-semibold text-emerald-400">{accuracy}%</span>
        </div>
      </div>
    </header>
  );
}
