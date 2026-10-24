import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Printer } from 'lucide-react';
import NotesHeader from '../components/NotesHeader.jsx';
import { fetchNotesIndex, fetchTopic } from '../services/notesService.js';

const inline = { p: ({ node, ...props }) => <span {...props} /> };

// Every note's TL;DR, keywords and traps on one printable page
export default function NotesCheatSheet() {
  const [domains, setDomains] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    document.title = 'Cheat sheet • SAA-C03 Notes';
    fetchNotesIndex()
      .then(async index => {
        const slugs = index.domains.flatMap(d => d.tasks.flatMap(t => t.topics)).filter(s => index.topics[s]);
        const notes = await Promise.all([...new Set(slugs)].map(s => fetchTopic(s).catch(() => null)));
        const bySlug = Object.fromEntries(notes.filter(Boolean).map(n => [n.slug, n]));
        setDomains(index.domains.map(d => ({
          ...d,
          notes: [...new Set(d.tasks.flatMap(t => t.topics))].map(s => bySlug[s]).filter(Boolean)
        })));
      })
      .catch(err => setError(err.message));
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 print:bg-white flex flex-col">
      <div className="print:hidden">
        <NotesHeader title="Cheat sheet" subtitle="TL;DR, keywords and traps from every note">
          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium bg-teal-600 text-white hover:bg-teal-500 transition"
          >
            <Printer className="w-4 h-4" /> Print
          </button>
        </NotesHeader>
      </div>

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 print:p-0 space-y-6">
        {error && <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl p-4 text-sm">{error}</div>}
        {!domains && !error && (
          <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-600 border-t-transparent" />
          </div>
        )}

        {domains?.map(d => d.notes.length > 0 && (
          <section key={d.id} className="space-y-3">
            <h2 className="text-lg font-bold text-slate-900 border-b border-slate-300 pb-1">
              D{d.id}: {d.name} <span className="font-mono text-sm font-normal text-slate-500">({d.weight}%)</span>
            </h2>
            <div className="grid gap-3 md:grid-cols-2 print:grid-cols-2">
              {d.notes.map(n => (
                <article key={n.slug} className="bg-white rounded-xl border border-slate-200 p-4 text-sm break-inside-avoid space-y-2">
                  <a href={`/notes/${n.slug}`} className="font-bold text-slate-900 hover:text-teal-700">
                    <span className="font-mono text-xs text-teal-700 mr-1.5">{n.task}</span>{n.title}
                  </a>
                  <ul className="list-disc pl-5 space-y-1 text-slate-700">
                    {(n.tldr || []).map((t, i) => <li key={i}><ReactMarkdown components={inline}>{t}</ReactMarkdown></li>)}
                  </ul>
                  {n.keywords?.length > 0 && (
                    <ul className="space-y-0.5 text-xs text-slate-600">
                      {n.keywords.map((k, i) => (
                        <li key={i}>“{k.cue}” → <strong className="text-teal-800">{k.answer}</strong></li>
                      ))}
                    </ul>
                  )}
                  {n.traps?.length > 0 && (
                    <ul className="list-disc pl-5 space-y-0.5 text-xs text-orange-900 bg-orange-50 rounded-lg py-2 pr-2">
                      {n.traps.map((t, i) => <li key={i}><ReactMarkdown components={inline}>{t}</ReactMarkdown></li>)}
                    </ul>
                  )}
                </article>
              ))}
            </div>
          </section>
        ))}
      </main>
    </div>
  );
}
