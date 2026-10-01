import React, { useState, useMemo } from 'react';
import { X, Search, Bookmark, CheckCircle2, XCircle, HelpCircle } from 'lucide-react';

export default function QuestionGridModal({
  isOpen,
  onClose,
  matrix,
  currentQuestionId,
  onSelectQuestion
}) {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const filteredMatrix = useMemo(() => {
    return matrix.filter(item => {
      // Search by ID
      if (search && !String(item.id).includes(search)) {
        return false;
      }
      if (filter === 'highlighted') return item.isHighlighted;
      if (filter === 'correct') return item.status === 'correct';
      if (filter === 'incorrect') return item.status === 'incorrect';
      if (filter === 'unattempted') return item.status === 'unattempted';
      return true;
    });
  }, [matrix, filter, search]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <h3 className="font-bold text-lg text-slate-900">
              Exam Questions Matrix
            </h3>
            <p className="text-xs text-slate-500">
              Overview of all 684 exam questions. Click any question to navigate directly.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filters & Search Toolbar */}
        <div className="px-6 py-3 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-white">
          
          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            {[
              { id: 'all', label: 'All (684)' },
              { id: 'highlighted', label: 'Highlighted' },
              { id: 'correct', label: 'Correct' },
              { id: 'incorrect', label: 'Incorrect' },
              { id: 'unattempted', label: 'Unattempted' },
            ].map(f => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  filter === f.id
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Search by question # */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Find question #..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-amber-500 w-36"
            />
          </div>
        </div>

        {/* Legend */}
        <div className="px-6 py-2 bg-slate-50/50 border-b border-slate-100 flex flex-wrap items-center gap-4 text-xs text-slate-500">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-emerald-500 inline-block" />
            <span>Correct</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-rose-500 inline-block" />
            <span>Incorrect</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-slate-100 border border-slate-300 inline-block" />
            <span>Unattempted</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded border-2 border-amber-500 bg-amber-50 inline-block" />
            <span>Highlighted (⭐️)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded ring-2 ring-blue-500 bg-white inline-block" />
            <span>Current Active</span>
          </div>
        </div>

        {/* Grid Matrix View */}
        <div className="p-6 overflow-y-auto flex-1 max-h-[60vh]">
          {filteredMatrix.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">
              No questions matched the current filter or search query.
            </div>
          ) : (
            <div className="grid grid-cols-6 sm:grid-cols-10 md:grid-cols-12 lg:grid-cols-14 gap-2">
              {filteredMatrix.map(item => {
                const isCurrent = item.id === currentQuestionId;
                
                let btnStyle = 'bg-slate-50 text-slate-700 hover:bg-slate-200 border border-slate-200';
                if (item.status === 'correct') {
                  btnStyle = 'bg-emerald-500 text-white font-bold hover:bg-emerald-600 shadow-xs';
                } else if (item.status === 'incorrect') {
                  btnStyle = 'bg-rose-500 text-white font-bold hover:bg-rose-600 shadow-xs';
                }

                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onSelectQuestion(item.id);
                      onClose();
                    }}
                    className={`relative h-10 rounded-lg text-xs font-mono font-medium transition flex items-center justify-center cursor-pointer ${btnStyle} ${
                      item.isHighlighted ? 'ring-2 ring-amber-400 ring-offset-1' : ''
                    } ${
                      isCurrent ? 'ring-3 ring-blue-600 ring-offset-2' : ''
                    }`}
                    title={`Question #${item.id} - ${item.status}${item.isHighlighted ? ' (Highlighted)' : ''}`}
                  >
                    {item.id}
                    {item.isHighlighted && (
                      <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-amber-500 rounded-full border border-white" />
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {filteredMatrix.length} questions</span>
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
