import React from 'react';
import ReactDOM from 'react-dom/client';
import { LogOut } from 'lucide-react';
import App from './App.jsx';
import ClaudeSetsIndex from './pages/ClaudeSetsIndex.jsx';
import ClaudeSetPage from './pages/ClaudeSetPage.jsx';
import NotesIndex from './pages/NotesIndex.jsx';
import NoteTopicPage from './pages/NoteTopicPage.jsx';
import NotesCheatSheet from './pages/NotesCheatSheet.jsx';
import { CLOUD, pullProgress, restoreSession, signIn, signOut } from './services/cloud.js';
import './index.css';

// Minimal path router: /claude -> set list, /claude/:id -> question set,
// /notes -> notes home, /notes/cheatsheet, /notes/:slug -> topic note, anything else -> main bank.
// Static hosts (CloudFront function / Express catch-all) already fall back to index.html.
function Root() {
  const path = window.location.pathname;
  const match = path.match(/^\/claude(?:\/([^/]+))?\/?$/);
  if (match) {
    return match[1] ? <ClaudeSetPage setId={match[1]} /> : <ClaudeSetsIndex />;
  }
  const notes = path.match(/^\/notes(?:\/([^/]+))?\/?$/);
  if (notes) {
    if (!notes[1]) return <NotesIndex />;
    return notes[1] === 'cheatsheet' ? <NotesCheatSheet /> : <NoteTopicPage slug={notes[1]} />;
  }
  return <App />;
}

function CenterCard({ children }) {
  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 w-full max-w-sm text-center space-y-4">
        {children}
      </div>
    </div>
  );
}

function SignInScreen() {
  return (
    <CenterCard>
      <h1 className="text-xl font-bold text-slate-900">AWS SAA-C03 Practice</h1>
      <p className="text-sm text-slate-600">Sign in to load the question bank and your progress.</p>
      <button
        type="button"
        onClick={() => signIn()}
        className="w-full px-4 py-2.5 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800 transition"
      >
        Sign in
      </button>
    </CenterCard>
  );
}

function ErrorScreen({ message }) {
  return (
    <CenterCard>
      <h1 className="text-lg font-bold text-slate-900">Couldn’t load your progress</h1>
      <p className="text-sm text-rose-700">{message}</p>
      <button
        type="button"
        onClick={() => window.location.reload()}
        className="w-full px-4 py-2.5 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800 transition"
      >
        Retry
      </button>
    </CenterCard>
  );
}

function SignOutButton({ email }) {
  return (
    <button
      type="button"
      onClick={() => signOut()}
      title={email ? `Signed in as ${email}` : 'Sign out'}
      className="fixed bottom-4 left-4 z-40 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-slate-900/90 text-slate-200 border border-slate-700 shadow-lg hover:bg-slate-800 hover:text-white transition"
    >
      <LogOut className="w-3.5 h-3.5" />
      Sign out
    </button>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
const render = (node) => root.render(<React.StrictMode>{node}</React.StrictMode>);

// Locally (no VITE_COGNITO_* in the build) the app renders straight away, as before.
// On AWS it signs in first and loads synced progress into localStorage before rendering.
async function boot() {
  if (!CLOUD) {
    render(<Root />);
    return;
  }

  let user;
  try {
    user = await restoreSession();
  } catch (err) {
    console.error('Sign-in failed:', err);
    user = null;
  }
  if (!user) {
    render(<SignInScreen />);
    return;
  }

  try {
    await pullProgress();
  } catch (err) {
    render(<ErrorScreen message={err.message} />);
    return;
  }

  render(
    <>
      <Root />
      <SignOutButton email={user.profile?.email} />
    </>,
  );
}

boot();
