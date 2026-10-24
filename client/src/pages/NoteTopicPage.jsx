import React, { useEffect, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { AlertTriangle, ArrowRight, Check, ChevronLeft } from 'lucide-react';
import NotesHeader from '../components/NotesHeader.jsx';
import {
  fetchNotesIndex,
  fetchTopic,
  fetchAllQuestions,
  questionsForNote,
  questionStatus,
  loadNotesProgress,
  toggleReviewed
} from '../services/notesService.js';

const DOMAIN_NAMES = {
  1: 'Design Secure Architectures',
  2: 'Design Resilient Architectures',
  3: 'Design High-Performing Architectures',
  4: 'Design Cost-Optimized Architectures'
};

// Inline markdown (bold, code, links) for the short strings in a note
function Md({ children }) {
  return (
    <ReactMarkdown
      components={{
        p: ({ node, ...props }) => <span {...props} />,
        code: ({ node, ...props }) => <code className="font-mono text-[0.9em] bg-slate-100 text-slate-800 px-1 rounded" {...props} />,
        a: ({ node, ...props }) => <a className="text-teal-700 underline" target="_blank" rel="noreferrer" {...props} />
      }}
    >
      {children}
    </ReactMarkdown>
  );
}

const STATUS_BADGE = {
  ok: { label: '✓', cls: 'bg-teal-100 text-teal-800', text: 'Answered correctly' },
  bad: { label: '✕', cls: 'bg-orange-100 text-orange-800', text: 'Answered wrong' },
  none: { label: '–', cls: 'bg-slate-100 text-slate-600', text: 'Not attempted' }
};

export default function NoteTopicPage({ slug }) {
  const [index, setIndex] = useState(null);
  const [note, setNote] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [error, setError] = useState(null);
  const [reviewed, setReviewed] = useState(() => loadNotesProgress().reviewed.includes(slug));

  useEffect(() => {
    fetchTopic(slug)
      .then(data => {
        setNote(data);
        document.title = `${data.title} • SAA-C03 Notes`;
      })
      .catch(err => setError(err.message));
    fetchNotesIndex().then(setIndex).catch(err => console.warn('Could not load notes index:', err));
    fetchAllQuestions().then(setQuestions).catch(err => console.warn('Could not load question sets:', err));
  }, [slug]);

  // Scroll to #section once the note has rendered
  useEffect(() => {
    if (note && window.location.hash) {
      document.getElementById(window.location.hash.slice(1))?.scrollIntoView();
    }
  }, [note]);

  const related = useMemo(() => {
    const entry = index?.topics?.[slug];
    if (!entry) return [];
    const progressBySet = {};
    return questionsForNote(entry, questions).map(q => ({ ...q, status: questionStatus(q, progressBySet) }));
  }, [index, slug, questions]);

  const attempted = related.filter(q => q.status !== 'none');
  const correct = attempted.filter(q => q.status === 'ok').length;
  // Wrong answers first, then unanswered, then correct
  const order = { bad: 0, none: 1, ok: 2 };
  const sortedRelated = [...related].sort((a, b) => order[a.status] - order[b.status]);
  const firstToDrill = sortedRelated.find(q => q.status !== 'ok') || sortedRelated[0];

  const sections = note
    ? [
        note.tldr?.length && ['tldr', 'TL;DR'],
        note.keyFacts?.length && ['facts', 'Key facts'],
        note.comparisons?.length && ['compare', 'Compare'],
        note.keywords?.length && ['keywords', 'Keywords → answer'],
        note.traps?.length && ['traps', 'Traps'],
        note.sections?.length && ['details', 'Details']
      ].filter(Boolean)
    : [];

  const relatedNotes = (note?.relatedNotes || []).filter(s => index?.topics?.[s]);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      <NotesHeader subtitle={note ? `Task ${note.task} • ${DOMAIN_NAMES[note.domain] || ''}` : undefined} />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
        <a href="/notes" className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-teal-700">
          <ChevronLeft className="w-4 h-4" /> All notes
        </a>

        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl p-4 text-sm">{error}</div>
        )}

        {!note && !error && (
          <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-600 border-t-transparent" />
          </div>
        )}

        {note && (
          <>
            <div className="flex flex-wrap items-end gap-4">
              <div className="flex-1 min-w-[16rem]">
                <div className="font-mono text-xs sm:text-sm text-teal-700 mb-1">
                  {note.task} • D{note.domain}: {DOMAIN_NAMES[note.domain]}
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{note.title}</h2>
                {note.summary && <p className="text-slate-600 mt-1">{note.summary}</p>}
                {note.services?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {note.services.map(s => (
                      <span key={s} className="text-xs text-slate-700 bg-slate-200 px-2.5 py-1 rounded-full">{s}</span>
                    ))}
                  </div>
                )}
              </div>
              <button
                type="button"
                aria-pressed={reviewed}
                onClick={() => setReviewed(toggleReviewed(slug).reviewed.includes(slug))}
                className={`inline-flex items-center gap-2 h-11 px-4 rounded-xl text-sm font-semibold border transition ${
                  reviewed
                    ? 'bg-teal-600 border-teal-600 text-white hover:bg-teal-700'
                    : 'bg-white border-slate-300 text-slate-900 hover:border-teal-500'
                }`}
              >
                <Check className="w-4 h-4" /> {reviewed ? 'Reviewed' : 'Mark as reviewed'}
              </button>
            </div>

            <div className="flex flex-col lg:flex-row gap-5 items-start">
              <div className="flex-1 min-w-0 w-full space-y-5">
                {note.tldr?.length > 0 && (
                  <section id="tldr" className="scroll-mt-24 bg-slate-900 text-slate-100 rounded-2xl p-5 sm:p-6">
                    <h3 className="text-xs font-semibold uppercase tracking-widest text-teal-300 mb-3">TL;DR</h3>
                    <ul className="list-disc pl-5 space-y-2 leading-relaxed [&_strong]:text-white">
                      {note.tldr.map((t, i) => <li key={i}><Md>{t}</Md></li>)}
                    </ul>
                  </section>
                )}

                {note.keyFacts?.length > 0 && (
                  <section id="facts" className="scroll-mt-24 bg-white rounded-2xl border border-slate-200 p-5 sm:p-6">
                    <h3 className="text-lg font-bold text-slate-900 mb-3">Key facts</h3>
                    <div className="grid gap-3 sm:grid-cols-2">
                      {note.keyFacts.map((f, i) => (
                        <div key={i} className="bg-slate-50 rounded-xl p-4">
                          <div className="font-mono text-lg text-teal-700">{f.value}</div>
                          <div className="text-sm text-slate-700 leading-relaxed mt-1"><Md>{f.text}</Md></div>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {note.comparisons?.map((c, ci) => (
                  <section key={ci} id={ci === 0 ? 'compare' : undefined} className="scroll-mt-24 bg-white rounded-2xl border border-slate-200 p-5 sm:p-6">
                    <h3 className="text-lg font-bold text-slate-900 mb-3">{c.title}</h3>
                    <div className="overflow-x-auto border border-slate-200 rounded-xl">
                      <table className="w-full min-w-[36rem] text-sm border-collapse">
                        <thead>
                          <tr className="bg-slate-50 text-left">
                            {c.columns.map(col => (
                              <th key={col} scope="col" className="px-3 py-2.5 font-semibold text-slate-700">{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {c.rows.map((row, ri) => (
                            <tr key={ri} className={`border-t border-slate-200 ${c.highlightRow === ri ? 'bg-teal-50' : ''}`}>
                              {row.map((cell, ki) => ki === 0 ? (
                                <th key={ki} scope="row" className="px-3 py-2.5 text-left font-semibold text-slate-900 align-top"><Md>{cell}</Md></th>
                              ) : (
                                <td key={ki} className="px-3 py-2.5 text-slate-700 align-top"><Md>{cell}</Md></td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </section>
                ))}

                {note.keywords?.length > 0 && (
                  <section id="keywords" className="scroll-mt-24 bg-white rounded-2xl border border-slate-200 p-5 sm:p-6">
                    <h3 className="text-lg font-bold text-slate-900 mb-3">Exam keywords → answer</h3>
                    <div className="space-y-2">
                      {note.keywords.map((k, i) => (
                        <div key={i} className="flex flex-wrap items-center gap-x-3 gap-y-1 bg-slate-50 rounded-lg px-3 py-2.5">
                          <span className="flex-1 min-w-[12rem] text-sm text-slate-700">“{k.cue}”</span>
                          <ArrowRight className="w-4 h-4 text-slate-500 shrink-0" aria-hidden="true" />
                          <span className="flex-1 min-w-[10rem] text-sm font-semibold text-teal-700"><Md>{k.answer}</Md></span>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {note.traps?.length > 0 && (
                  <section id="traps" className="scroll-mt-24 bg-orange-50 rounded-2xl border border-orange-200 p-5 sm:p-6">
                    <h3 className="text-lg font-bold text-orange-900 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" /> Traps
                    </h3>
                    <ul className="list-disc pl-5 space-y-2 text-sm leading-relaxed text-orange-950">
                      {note.traps.map((t, i) => <li key={i}><Md>{t}</Md></li>)}
                    </ul>
                  </section>
                )}

                {note.sections?.length > 0 && (
                  <section id="details" className="scroll-mt-24 bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 space-y-5">
                    {note.sections.map((s, i) => (
                      <div key={i}>
                        <h3 className="text-lg font-bold text-slate-900 mb-2">{s.heading}</h3>
                        <div className="text-sm text-slate-700 leading-relaxed space-y-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_strong]:text-slate-900 [&_code]:font-mono [&_code]:bg-slate-100 [&_code]:px-1 [&_code]:rounded">
                          <ReactMarkdown>{s.body}</ReactMarkdown>
                        </div>
                      </div>
                    ))}
                  </section>
                )}

                {note.sources?.length > 0 && (
                  <p className="text-xs text-slate-500">
                    Sources:{' '}
                    {note.sources.map((s, i) => (
                      <a key={i} href={s.url} target="_blank" rel="noreferrer" className="underline hover:text-slate-700 mr-2">{s.title}</a>
                    ))}
                  </p>
                )}
              </div>

              <aside className="w-full lg:w-80 shrink-0 space-y-4 lg:sticky lg:top-24">
                <section className="bg-white rounded-2xl border border-slate-200 p-5">
                  <div className="flex items-baseline justify-between gap-2">
                    <h3 className="font-bold text-slate-900">Related questions</h3>
                    {attempted.length > 0 && (
                      <span className={`font-mono text-xs ${correct / attempted.length < 0.65 ? 'text-orange-700' : 'text-teal-700'}`}>
                        {correct} / {attempted.length} correct
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mb-3">Practice-set questions tagged with this topic</p>
                  {related.length === 0 ? (
                    <p className="text-sm text-slate-500">No tagged questions yet.</p>
                  ) : (
                    <div className="space-y-1.5 max-h-[28rem] overflow-y-auto pr-1">
                      {sortedRelated.map(q => {
                        const badge = STATUS_BADGE[q.status];
                        return (
                          <a
                            key={`${q.setId}-${q.id}`}
                            href={`/claude/${q.setId}?q=${q.id}`}
                            className="flex gap-2.5 items-start p-2 rounded-lg border border-slate-100 hover:border-teal-400 transition"
                          >
                            <span title={badge.text} className={`w-5 h-5 shrink-0 rounded-full flex items-center justify-center text-[11px] font-bold ${badge.cls}`}>
                              <span aria-hidden="true">{badge.label}</span>
                              <span className="sr-only">{badge.text}</span>
                            </span>
                            <span className="min-w-0">
                              <span className="block font-mono text-[11px] text-slate-500">Set {q.setId} • Q{q.id}</span>
                              <span className="text-xs text-slate-700 leading-snug line-clamp-2">{q.prompt}</span>
                            </span>
                          </a>
                        );
                      })}
                    </div>
                  )}
                  {firstToDrill && (
                    <a
                      href={`/claude/${firstToDrill.setId}?q=${firstToDrill.id}`}
                      className="mt-3 flex items-center justify-center h-11 rounded-xl bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition"
                    >
                      Drill these questions
                    </a>
                  )}
                </section>

                {sections.length > 1 && (
                  <nav aria-label="On this page" className="bg-white rounded-2xl border border-slate-200 p-5 text-sm">
                    <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">On this page</div>
                    {sections.map(([id, label]) => (
                      <a key={id} href={`#${id}`} className="block py-1 text-teal-700 hover:text-teal-900">{label}</a>
                    ))}
                  </nav>
                )}

                {relatedNotes.length > 0 && (
                  <section className="bg-white rounded-2xl border border-slate-200 p-5">
                    <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">See also</div>
                    <div className="flex flex-wrap gap-1.5">
                      {relatedNotes.map(s => (
                        <a key={s} href={`/notes/${s}`} className="text-xs font-medium px-2.5 py-1 rounded-full border bg-teal-50 border-teal-200 text-teal-900 hover:border-teal-500">
                          {index.topics[s].title}
                        </a>
                      ))}
                    </div>
                  </section>
                )}
              </aside>
            </div>
          </>
        )}
      </main>

      <footer className="py-6 border-t border-slate-200/80 text-center text-xs text-slate-400">
        Generated study notes • Not official AWS exam content
      </footer>
    </div>
  );
}
