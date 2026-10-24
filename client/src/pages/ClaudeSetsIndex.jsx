import React, { useEffect, useState } from 'react';
import { ArrowRight, Clock, Target, ListChecks, Layers } from 'lucide-react';
import ClaudeHeader from '../components/ClaudeHeader.jsx';
import { fetchSetIndex, loadProgress } from '../services/claudeSetService.js';

export default function ClaudeSetsIndex() {
  const [index, setIndex] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSetIndex().then(setIndex).catch(err => setError(err.message));
  }, []);

  const format = index?.examFormat;

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      <ClaudeHeader title="Claude Practice Sets" subtitle="Freshly generated SAA-C03 mock exams aligned to the current exam guide">
        <a href="/notes" className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-teal-300 hover:text-teal-200 transition">
          Notes
        </a>
      </ClaudeHeader>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl p-4 text-sm">{error}</div>
        )}

        {!index && !error && (
          <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-violet-500 border-t-transparent" />
          </div>
        )}

        {format && (
          <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <h2 className="font-bold text-slate-900 mb-1">Current exam format ({format.examCode})</h2>
            <p className="text-sm text-slate-500 mb-4">Exam guide checked {format.verifiedOn}. Each set below mirrors this blueprint.</p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
              <Stat icon={ListChecks} label="Questions" value={`${format.totalQuestions}`} hint={`${format.scoredQuestions} scored + ${format.unscoredQuestions} unscored`} />
              <Stat icon={Clock} label="Duration" value={`${format.durationMinutes} min`} />
              <Stat icon={Target} label="Passing score" value={`${format.passingScore}`} hint={`scaled ${format.scoreRange}`} />
              <Stat icon={Layers} label="Response types" value="2" hint="single & multiple response" />
            </div>
            <div className="space-y-2">
              {format.domains.map(d => (
                <div key={d.id} className="flex items-center gap-3 text-sm">
                  <span className="w-48 sm:w-72 text-slate-700 truncate">D{d.id}: {d.name}</span>
                  <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-violet-500" style={{ width: `${d.weight * 3}%` }} />
                  </div>
                  <span className="w-10 text-right font-mono text-slate-600">{d.weight}%</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {index?.sets?.map(set => {
          const progress = loadProgress(set.id);
          const attempted = Object.keys(progress.attempts).length;
          const pct = Math.round((attempted / set.questionCount) * 100);
          return (
            <a
              key={set.id}
              href={`/claude/${set.id}`}
              className="block bg-white rounded-2xl shadow-sm border border-slate-200 p-6 hover:border-violet-400 hover:shadow-md transition group"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <span className="text-xs font-mono font-semibold text-violet-700 bg-violet-50 border border-violet-200 px-2 py-0.5 rounded">
                    /claude/{set.id}
                  </span>
                  <h3 className="font-bold text-lg text-slate-900 mt-2">{set.title}</h3>
                  <p className="text-sm text-slate-600 mt-1">{set.description}</p>
                  <p className="text-xs text-slate-500 mt-3">
                    {set.questionCount} questions • {set.multiCount} multiple response • Domains {set.domainCounts.map((c, i) => `D${i + 1}:${c}`).join(' / ')}
                  </p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-violet-600 shrink-0 mt-1" />
              </div>
              <div className="mt-4 flex items-center gap-3 text-xs text-slate-500">
                <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500" style={{ width: `${pct}%` }} />
                </div>
                <span>{attempted}/{set.questionCount} attempted</span>
              </div>
            </a>
          );
        })}

        {index?.sources && (
          <p className="text-xs text-slate-400">
            Source: {index.sources.map((s, i) => (
              <a key={i} href={s.url} target="_blank" rel="noreferrer" className="underline hover:text-slate-600 mr-2">{s.title}</a>
            ))}
          </p>
        )}
      </main>
    </div>
  );
}

function Stat({ icon: Icon, label, value, hint }) {
  return (
    <div className="bg-slate-50 rounded-xl border border-slate-200 p-3">
      <div className="flex items-center gap-1.5 text-xs text-slate-500"><Icon className="w-3.5 h-3.5" />{label}</div>
      <div className="font-bold text-slate-900 text-lg">{value}</div>
      {hint && <div className="text-[11px] text-slate-500">{hint}</div>}
    </div>
  );
}
