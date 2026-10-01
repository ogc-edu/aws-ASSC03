import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Bookmark, 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  ArrowRight, 
  RotateCcw, 
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp,
  Pin
} from 'lucide-react';

export default function QuestionCard({
  question,
  onAttempt,
  onToggleHighlight,
  onResetQuestion,
  onNext,
  onPrev,
  isFirst,
  isLast,
  isLeftOff
}) {
  const [selected, setSelected] = useState([]);
  const [showFullExplanation, setShowFullExplanation] = useState(true);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [localExplanation, setLocalExplanation] = useState(question?.explanation);

  useEffect(() => {
    setLocalExplanation(question?.explanation);
  }, [question?.id, question?.explanation]);

  const handleGenerateAIDeepDive = async (e) => {
    e.stopPropagation();
    try {
      setIsGeneratingAI(true);
      const res = await fetch(`/api/questions/${question.id}/ai-explain`, { method: 'POST' });
      const data = await res.json();
      if (data.explanation) {
        setLocalExplanation(data.explanation);
        question.explanation = data.explanation;
      }
    } catch (err) {
      console.error('Failed to generate AI deep dive:', err);
    } finally {
      setIsGeneratingAI(false);
    }
  };

  // Sync selected answers with question's attempt state
  useEffect(() => {
    if (question?.attempt?.selected) {
      setSelected(question.attempt.selected);
    } else {
      setSelected([]);
    }
  }, [question?.id, question?.attempt]);

  if (!question) {
    return (
      <div className="flex items-center justify-center p-12 bg-white rounded-2xl shadow-sm border border-slate-200">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Loading question...</p>
        </div>
      </div>
    );
  }

  const isAttempted = !!question.attempt;
  const isCorrect = question.attempt?.isCorrect;
  const correctAnswers = question.correctAnswers || [];
  const requiredCount = question.requiredCount || 1;
  const isMulti = question.isMulti || requiredCount > 1;

  // Handle option click
  const handleOptionClick = (letter) => {
    if (isAttempted) return; // Prevent changing after attempted unless user resets

    if (isMulti) {
      let updated;
      if (selected.includes(letter)) {
        updated = selected.filter(l => l !== letter);
      } else {
        if (selected.length < requiredCount) {
          updated = [...selected, letter];
        } else {
          // Replace last or don't allow exceeding
          updated = [...selected.slice(1), letter];
        }
      }
      setSelected(updated);
    } else {
      // Single choice: immediate submission
      const newSelected = [letter];
      setSelected(newSelected);
      onAttempt(question.id, newSelected);
    }
  };

  const handleMultiSubmit = () => {
    if (selected.length === requiredCount) {
      onAttempt(question.id, selected);
    }
  };

  const optionsList = Object.entries(question.options || {}).sort(([a], [b]) => a.localeCompare(b));

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden transition-all duration-200">
      
      {/* Top Question Header Bar */}
      <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <span className="font-mono text-sm font-bold text-slate-700 bg-white px-3 py-1 rounded-lg border border-slate-200 shadow-xs">
            Question #{question.id}
          </span>

          {/* Type Badge */}
          {isMulti ? (
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              Multiple Choice • Select {requiredCount}
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-200/60 text-slate-700">
              Single Choice
            </span>
          )}

          {/* Left-off Pin marker */}
          {isLeftOff && (
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200" title="Your saved left-off question">
              <Pin className="w-3 h-3 text-amber-600" />
              <span>Current Left-off</span>
            </span>
          )}
        </div>

        {/* Highlight / Bookmark Toggle Button */}
        <button
          onClick={() => onToggleHighlight(question.id)}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
            question.isHighlighted
              ? 'bg-amber-50 border-amber-300 text-amber-800 shadow-xs'
              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'
          }`}
          title="Toggle highlight (shortcut: H)"
        >
          <Bookmark className={`w-4 h-4 ${question.isHighlighted ? 'text-amber-500 fill-amber-500' : 'text-slate-400'}`} />
          <span>{question.isHighlighted ? 'Highlighted' : 'Highlight'}</span>
        </button>
      </div>

      {/* Main Content Area */}
      <div className="p-6 sm:p-8">
        
        {/* Question Prompt */}
        <div className="text-slate-800 text-base sm:text-lg leading-relaxed font-normal mb-8 select-text">
          {question.prompt}
        </div>

        {/* Options List */}
        <div className="space-y-3 mb-6">
          {optionsList.map(([letter, text]) => {
            const isSelected = selected.includes(letter);
            const isCorrectOption = correctAnswers.includes(letter);

            // Determine styling based on attempt status
            let cardStyle = 'border-slate-200 bg-white hover:border-amber-400 hover:bg-amber-50/20';
            let badgeStyle = 'bg-slate-100 text-slate-700 border-slate-200';
            let icon = null;

            if (isAttempted) {
              if (isSelected && isCorrectOption) {
                // Correct pick!
                cardStyle = 'border-emerald-500 bg-emerald-50/70 text-emerald-950 font-medium ring-1 ring-emerald-500/30';
                badgeStyle = 'bg-emerald-600 text-white border-emerald-600';
                icon = <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 ml-auto" />;
              } else if (isSelected && !isCorrectOption) {
                // Wrong pick!
                cardStyle = 'border-rose-400 bg-rose-50/70 text-rose-950 font-medium ring-1 ring-rose-400/30';
                badgeStyle = 'bg-rose-500 text-white border-rose-500';
                icon = <XCircle className="w-5 h-5 text-rose-500 shrink-0 ml-auto" />;
              } else if (!isSelected && isCorrectOption) {
                // Correct option that was not selected by user
                cardStyle = 'border-emerald-500 bg-emerald-50/30 border-dashed text-emerald-950';
                badgeStyle = 'bg-emerald-100 text-emerald-800 border-emerald-400';
                icon = (
                  <span className="text-xs font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded shrink-0 ml-auto">
                    Correct Option
                  </span>
                );
              } else {
                // Neutral unselected
                cardStyle = 'border-slate-200 bg-slate-50/40 text-slate-500 opacity-60';
                badgeStyle = 'bg-slate-100 text-slate-400 border-slate-200';
              }
            } else if (isSelected) {
              // Pre-attempt selected state (mainly for multi-choice)
              cardStyle = 'border-amber-500 bg-amber-50/40 text-slate-900 ring-1 ring-amber-500/30';
              badgeStyle = 'bg-amber-500 text-slate-950 font-bold border-amber-500';
            }

            return (
              <button
                key={letter}
                onClick={() => handleOptionClick(letter)}
                disabled={isAttempted}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-150 flex items-start space-x-4 cursor-pointer ${cardStyle} ${
                  isAttempted ? 'cursor-default' : ''
                }`}
              >
                {/* Letter Identifier */}
                <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm shrink-0 border ${badgeStyle}`}>
                  {letter}
                </span>

                {/* Option Text */}
                <div className="flex-1 text-sm sm:text-base leading-snug pt-0.5">
                  {text}
                </div>

                {/* Status Indicator Icon */}
                {icon}
              </button>
            );
          })}
        </div>

        {/* Multi-choice Submission Button */}
        {isMulti && !isAttempted && (
          <div className="flex items-center justify-between bg-slate-50 p-4 rounded-xl border border-slate-200 mb-6">
            <span className="text-sm text-slate-600">
              Selected <span className="font-semibold text-slate-900">{selected.length}</span> of {requiredCount} options required
            </span>
            <button
              onClick={handleMultiSubmit}
              disabled={selected.length !== requiredCount}
              className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition shadow-sm ${
                selected.length === requiredCount
                  ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 cursor-pointer shadow-amber-500/20'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }`}
            >
              Submit Answer
            </button>
          </div>
        )}

        {/* Immediate Result Banner & Explanation Box (Revealed after attempt) */}
        {isAttempted && (
          <div className="mt-8 pt-6 border-t border-slate-200 space-y-5 animate-in fade-in duration-200">
            
            {/* Feedback Status Header */}
            <div className={`p-4 rounded-xl flex items-center justify-between ${
              isCorrect ? 'bg-emerald-50 border border-emerald-200' : 'bg-rose-50 border border-rose-200'
            }`}>
              <div className="flex items-center space-x-3">
                {isCorrect ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
                ) : (
                  <XCircle className="w-6 h-6 text-rose-500 shrink-0" />
                )}
                <div>
                  <h4 className={`font-bold text-base ${isCorrect ? 'text-emerald-900' : 'text-rose-900'}`}>
                    {isCorrect ? 'Correct Answer!' : 'Incorrect'}
                  </h4>
                  <p className={`text-xs sm:text-sm ${isCorrect ? 'text-emerald-700' : 'text-rose-700'}`}>
                    Correct Solution: <span className="font-bold underline uppercase">{correctAnswers.join(', ')}</span>
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onResetQuestion(question.id)}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition shadow-xs"
                  title="Try answering this question again"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Try Again</span>
                </button>

                {!isLast && (
                  <button
                    onClick={onNext}
                    className="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg text-xs sm:text-sm font-semibold bg-slate-900 text-white hover:bg-slate-800 transition shadow-sm"
                  >
                    <span>Next</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Detailed Architecture Solution Box */}
            <div className="bg-slate-900 text-slate-100 rounded-xl overflow-hidden border border-slate-800 shadow-md">
              <div 
                onClick={() => setShowFullExplanation(!showFullExplanation)}
                className="px-5 py-3.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between cursor-pointer select-none flex-wrap gap-2"
              >
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span className="font-semibold text-sm text-slate-200">
                    Architectural Solution & Concepts
                  </span>
                  {localExplanation?.includes('Why Option') && (
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Option-by-Option Deep Dive
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleGenerateAIDeepDive}
                    disabled={isGeneratingAI}
                    className="flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition"
                    title="Generate an exhaustive option-by-option architectural breakdown"
                  >
                    {isGeneratingAI ? (
                      <>
                        <div className="w-3 h-3 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
                        <span>Analyzing All Options...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        <span>Deep Dive Analysis</span>
                      </>
                    )}
                  </button>

                  <button className="text-slate-400 hover:text-slate-200">
                    {showFullExplanation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {showFullExplanation && (
                <div className="p-5 sm:p-6 text-sm text-slate-300 leading-relaxed font-sans space-y-3">
                  <ReactMarkdown
                    components={{
                      h3: ({ node, ...props }) => (
                        <h3 className="text-sm sm:text-base font-bold text-amber-400 mt-4 first:mt-0 mb-2 pb-1 border-b border-slate-800 flex items-center space-x-1.5" {...props} />
                      ),
                      strong: ({ node, ...props }) => (
                        <strong className="font-semibold text-slate-100" {...props} />
                      ),
                      p: ({ node, ...props }) => (
                        <p className="mb-2.5 text-slate-300 leading-relaxed" {...props} />
                      ),
                      ul: ({ node, ...props }) => (
                        <ul className="space-y-2 my-2 list-none pl-0" {...props} />
                      ),
                      li: ({ node, ...props }) => (
                        <li className="text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 leading-snug" {...props} />
                      ),
                      hr: ({ node, ...props }) => (
                        <hr className="my-4 border-slate-800" {...props} />
                      )
                    }}
                  >
                    {localExplanation || question.explanation}
                  </ReactMarkdown>
                </div>
              )}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
