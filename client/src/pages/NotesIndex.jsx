import React, { useEffect, useMemo, useState } from 'react';
import { Search, Printer, CheckCircle2 } from 'lucide-react';
import NotesHeader from '../components/NotesHeader.jsx';
import {
  fetchNotesIndex,
  fetchAllQuestions,
  questionsForNote,
  scoreQuestions,
  loadNotesProgress,
  matchesSearch
} from '../services/notesService.js';

export default function NotesIndex() {
  const [index, setIndex] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState('');
  const reviewed = useMemo(() => new Set(loadNotesProgress().reviewed), []);

  useEffect(() => {
    document.title = 'Notes • SAA-C03';
    fetchNotesIndex().then(setIndex).catch(err => setError(err.message));
    // Question sets only feed the accuracy figures, so the page still works without them.
    fetchAllQuestions().then(setQuestions).catch(err => console.warn('Could not load question sets:', err));
  }, []);

  // Per-note score over the questions tagged with its topics
  const noteStats = useMemo(() => {
    if (!index) return {};
    const progressBySet = {};
    return Object.fromEntries(
      Object.entries(index.topics).map(([slug, t]) => [slug, scoreQuestions(questionsForNote(t, questions), progressBySet)])
    );
  }, [index, questions]);

  const taskStats = useMemo(() => {
    const progressBySet = {};
    const byTask = {};
    for (const q of questions) (byTask[q.task] ||= []).push(q);
    return Object.fromEntries(Object.entries(byTask).map(([task, qs]) => [task, scoreQuestions(qs, progressBySet)]));
  }, [questions]);

  const weakest = useMemo(() => {
    if (!index) return [];
    return Object.entries(noteStats)
      .filter(([, s]) => s.wrong > 0)
      .sort(([, a], [, b]) => b.wrong - a.wrong || a.accuracy - b.accuracy)
      .slice(0, 4)
      .map(([slug, s]) => ({ slug, ...index.topics[slug], stats: s }));
  }, [index, noteStats]);

  const searchResults = useMemo(() => {
    if (!index || !query.trim()) return null;
    return Object.entries(index.topics)
      .filter(([slug, t]) => matchesSearch(slug, t, query))
      .map(([slug, t]) => ({ slug, ...t }));
  }, [index, query]);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      <NotesHeader subtitle="Study notes mapped to the exam guide and linked to your practice questions" />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl p-4 text-sm">{error}</div>
        )}

        {!index && !error && (
          <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-600 border-t-transparent" />
          </div>
        )}

        {index && (
          <>
            <div className="flex flex-wrap gap-3">
              <label className="flex-1 min-w-[16rem] flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-4 h-12 focus-within:border-teal-500">
                <Search className="w-4 h-4 text-slate-500 shrink-0" aria-hidden="true" />
                <span className="sr-only">Search notes</span>
                <input
                  type="search"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Search services, keywords, traps… e.g. “single-tenant HSM”"
                  className="flex-1 bg-transparent outline-none text-sm sm:text-base text-slate-900 placeholder:text-slate-400"
                />
              </label>
              <a
                href="/notes/cheatsheet"
                className="inline-flex items-center gap-2 h-12 px-4 rounded-xl bg-white border border-slate-200 text-sm font-semibold text-slate-900 hover:border-teal-500 transition"
              >
                <Printer className="w-4 h-4" /> Cheat sheet
              </a>
            </div>

            {searchResults ? (
              <section className="space-y-3">
                <h2 className="text-sm text-slate-600">
                  {searchResults.length} {searchResults.length === 1 ? 'note matches' : 'notes match'} “{query.trim()}”
                </h2>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {searchResults.map(t => (
                    <a key={t.slug} href={`/notes/${t.slug}`} className="block bg-white rounded-xl border border-slate-200 p-4 hover:border-teal-500 transition">
                      <span className="font-mono text-xs text-teal-700">{t.task}</span>
                      <h3 className="font-semibold text-slate-900">{t.title}</h3>
                      {t.summary && <p className="text-sm text-slate-600 mt-1">{t.summary}</p>}
                    </a>
                  ))}
                </div>
              </section>
            ) : (
              <>
                {weakest.length > 0 && (
                  <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 mb-4">
                      <h2 className="font-bold text-slate-900">Study next</h2>
                      <span className="text-sm text-slate-500">Topics ranked by your wrong answers across the practice sets</span>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                      {weakest.map(t => (
                        <a key={t.slug} href={`/notes/${t.slug}`} className="block rounded-xl border border-slate-200 bg-slate-50 p-4 hover:border-orange-400 transition space-y-2">
                          <div className="flex justify-between gap-2">
                            <span className="font-semibold text-sm text-slate-900">{t.title}</span>
                            <span className="font-mono text-xs text-orange-700">{t.stats.accuracy}%</span>
                          </div>
                          <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div className="h-full bg-orange-500" style={{ width: `${t.stats.accuracy}%` }} />
                          </div>
                          <div className="text-xs text-slate-500">
                            Task {t.task} • {t.stats.wrong} of {t.stats.attempted} wrong
                          </div>
                        </a>
                      ))}
                    </div>
                  </section>
                )}

                {index.domains.map(d => (
                  <section key={d.id} className="space-y-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="font-mono text-xs font-semibold text-white bg-slate-900 px-2 py-1 rounded-md">D{d.id}</span>
                      <h2 className="text-lg font-bold text-slate-900">{d.name}</h2>
                      <div className="flex-1 min-w-[6rem] h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div className="h-full bg-teal-600" style={{ width: `${d.weight * 3}%` }} />
                      </div>
                      <span className="font-mono text-sm text-slate-600">{d.weight}% of exam</span>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                      {d.tasks.map(task => {
                        const slugs = task.topics.filter(s => index.topics[s]);
                        const done = slugs.filter(s => reviewed.has(s)).length;
                        const ts = taskStats[task.id];
                        return (
                          <article key={task.id} className="bg-white rounded-xl border border-slate-200 p-4 flex flex-col gap-3">
                            <div className="flex gap-2">
                              <span className="font-mono text-xs text-teal-700 pt-0.5">{task.id}</span>
                              <h3 className="text-sm font-semibold text-slate-900 leading-snug">{task.name}</h3>
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                              {slugs.length === 0 && <span className="text-xs text-slate-400">No notes yet</span>}
                              {slugs.map(s => (
                                <a
                                  key={s}
                                  href={`/notes/${s}`}
                                  className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full border transition ${
                                    reviewed.has(s)
                                      ? 'bg-teal-600 border-teal-600 text-white hover:bg-teal-700'
                                      : 'bg-teal-50 border-teal-200 text-teal-900 hover:border-teal-500'
                                  }`}
                                >
                                  {reviewed.has(s) && <CheckCircle2 className="w-3 h-3" />}
                                  {index.topics[s].title}
                                </a>
                              ))}
                            </div>
                            <div className="mt-auto flex justify-between text-xs text-slate-500 border-t border-slate-100 pt-2">
                              <span>{done} / {slugs.length} notes reviewed</span>
                              {ts?.accuracy != null && (
                                <span className={`font-semibold ${ts.accuracy < 65 ? 'text-orange-700' : 'text-teal-700'}`}>
                                  {ts.accuracy}% correct
                                </span>
                              )}
                            </div>
                          </article>
                        );
                      })}
                    </div>
                  </section>
                ))}
              </>
            )}
          </>
        )}
      </main>

      <footer className="py-6 border-t border-slate-200/80 text-center text-xs text-slate-400">
        Generated study notes • Not official AWS exam content
      </footer>
    </div>
  );
}
