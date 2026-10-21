import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import ClaudeSetsIndex from './pages/ClaudeSetsIndex.jsx';
import ClaudeSetPage from './pages/ClaudeSetPage.jsx';
import './index.css';

// Minimal path router: /claude -> set list, /claude/:id -> question set, anything else -> main bank.
// Static hosts (S3 error document / Express catch-all) already fall back to index.html.
function Root() {
  const match = window.location.pathname.match(/^\/claude(?:\/([^/]+))?\/?$/);
  if (match) {
    return match[1] ? <ClaudeSetPage setId={match[1]} /> : <ClaudeSetsIndex />;
  }
  return <App />;
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
