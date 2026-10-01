import React from 'react';
import { X, Bookmark, ExternalLink, Trash2, CheckCircle2, XCircle } from 'lucide-react';

export default function HighlightsModal({
  isOpen,
  onClose,
  highlightedQuestions,
  onSelectQuestion,
  onRemoveHighlight,
  attempts
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-amber-500/10">
          <div className="flex items-center space-x-2">
            <Bookmark className="w-5 h-5 text-amber-500 fill-amber-500" />
            <h3 className="font-bold text-lg text-slate-900">
              Highlighted Questions ({highlightedQuestions.length})
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200/50 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content List */}
        <div className="p-6 overflow-y-auto flex-1 space-y-3">
          {highlightedQuestions.length === 0 ? (
            <div className="text-center py-16 px-4">
              <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Bookmark className="w-6 h-6 text-amber-500" />
              </div>
              <h4 className="font-semibold text-slate-800 text-base mb-1">
                No Highlighted Questions Yet
              </h4>
              <p className="text-sm text-slate-500 max-w-sm mx-auto">
                While practicing, click the <strong>Highlight</strong> button or press <kbd className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-700 border text-xs">H</kbd> on any question to bookmark it for focused review.
              </p>
            </div>
          ) : (
            highlightedQuestions.map((q) => {
              const attempt = attempts[q.id];
              let statusBadge = null;
              if (attempt) {
                if (attempt.isCorrect) {
                  statusBadge = (
                    <span className="inline-flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" /> Correct
                    </span>
                  );
                } else {
                  statusBadge = (
                    <span className="inline-flex items-center text-xs font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                      <XCircle className="w-3 h-3 mr-1 text-rose-500" /> Missed
                    </span>
                  );
                }
              } else {
                statusBadge = (
                  <span className="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    Unattempted
                  </span>
                );
              }

              return (
                <div 
                  key={q.id}
                  className="p-4 rounded-xl border border-slate-200 hover:border-amber-400 bg-white transition flex items-start justify-between gap-4 group"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2.5 mb-1.5">
                      <span className="font-mono text-xs font-bold bg-slate-100 text-slate-800 px-2 py-0.5 rounded border border-slate-200">
                        Q#{q.id}
                      </span>
                      {statusBadge}
                      {q.isMulti && (
                        <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                          Multi-choice
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-700 line-clamp-2">
                      {q.prompt}
                    </p>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <button
                      onClick={() => {
                        onSelectQuestion(q.id);
                        onClose();
                      }}
                      className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-medium transition flex items-center space-x-1"
                    >
                      <span>Practice</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => onRemoveHighlight(q.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition"
                      title="Remove from highlights"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>{highlightedQuestions.length} bookmarked questions</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition font-medium"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
