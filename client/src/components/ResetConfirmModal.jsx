import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

export default function ResetConfirmModal({
  isOpen,
  onClose,
  onConfirmReset
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-md p-6 overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">
              Reset Practice Progress
            </h3>
            <p className="text-xs text-slate-500">
              Choose which progress data you would like to clear.
            </p>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          <button
            onClick={() => {
              onConfirmReset('attempts-only');
              onClose();
            }}
            className="w-full text-left p-3.5 rounded-xl border border-slate-200 hover:border-amber-400 hover:bg-amber-50/20 transition"
          >
            <div className="font-semibold text-sm text-slate-800">
              Reset Answers & Scores Only
            </div>
            <div className="text-xs text-slate-500">
              Keeps all your highlighted questions intact, but clears test attempts.
            </div>
          </button>

          <button
            onClick={() => {
              onConfirmReset('all');
              onClose();
            }}
            className="w-full text-left p-3.5 rounded-xl border border-rose-200 hover:border-rose-400 hover:bg-rose-50/30 transition"
          >
            <div className="font-semibold text-sm text-rose-700">
              Full Factory Reset
            </div>
            <div className="text-xs text-slate-500">
              Wipes all attempts, highlights, and resets back to Question #1.
            </div>
          </button>
        </div>

        <div className="flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
