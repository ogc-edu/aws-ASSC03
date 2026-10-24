import React from 'react';
import { BookOpen } from 'lucide-react';

const NAV = [
  { href: '/', label: 'Question bank' },
  { href: '/claude', label: 'Practice sets' },
  { href: '/notes', label: 'Notes' }
];

// Shared top bar for the /notes pages
export default function NotesHeader({ title = 'SAA-C03 Notes', subtitle, children }) {
  return (
    <header className="sticky top-0 z-30 bg-slate-900 border-b border-slate-800 text-white shadow-md">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center justify-between min-h-16 py-2 gap-3">
          <a href="/notes" className="flex items-center space-x-3 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-teal-600 flex items-center justify-center shadow-lg shadow-teal-500/20 shrink-0">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="font-bold text-base sm:text-lg text-slate-100 leading-tight truncate">{title}</h1>
              {subtitle && <p className="text-xs text-slate-400 hidden sm:block truncate">{subtitle}</p>}
            </div>
          </a>

          <nav aria-label="Sections" className="flex items-center gap-1">
            {children}
            {NAV.map(item => {
              const active = item.href === '/notes';
              return (
                <a
                  key={item.href}
                  href={item.href}
                  aria-current={active ? 'page' : undefined}
                  className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition ${
                    active ? 'bg-slate-800 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {item.label}
                </a>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
