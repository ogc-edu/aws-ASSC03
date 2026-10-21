import React from 'react';
import { ArrowLeft, Sparkles } from 'lucide-react';

// Shared top bar for the Claude-generated question set pages
export default function ClaudeHeader({ title, subtitle, backHref = '/', backLabel = 'Main Question Bank', children }) {
  return (
    <header className="sticky top-0 z-30 bg-slate-900 border-b border-slate-800 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          <div className="flex items-center space-x-3 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-500 to-fuchsia-400 flex items-center justify-center shadow-lg shadow-violet-500/20 shrink-0">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="font-bold text-base sm:text-lg text-slate-100 leading-tight truncate">{title}</h1>
              {subtitle && <p className="text-xs text-slate-400 hidden sm:block truncate">{subtitle}</p>}
            </div>
          </div>

          <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
            {children}
            <a
              href={backHref}
              className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition"
            >
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span className="hidden sm:inline">{backLabel}</span>
              <span className="sm:hidden">Back</span>
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
