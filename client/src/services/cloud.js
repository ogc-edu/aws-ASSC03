// client/src/services/cloud.js
// Cloud mode (saa.<domain> on AWS): Cognito sign-in, question files fetched through the API,
// and progress synced to DynamoDB. Enabled only when the build has VITE_COGNITO_* set, so the
// local Express setup (npm run dev / npm start) keeps working unchanged.
//
// localStorage stays the working copy that the rest of the app reads synchronously:
// pullProgress() fills it from the server before the app renders, and pushProgress()
// sends each change back.

import { UserManager } from 'oidc-client-ts';

const env = import.meta.env;

export const CLOUD = Boolean(env.VITE_COGNITO_AUTHORITY && env.VITE_COGNITO_CLIENT_ID && env.VITE_COGNITO_DOMAIN);

const PROGRESS_PREFIX = 'aws_saa_c03_';
const PUSH_DELAY_MS = 800;

const appOrigin = () => `${window.location.origin}/`;

export const userManager = CLOUD
  ? new UserManager({
      authority: env.VITE_COGNITO_AUTHORITY,
      client_id: env.VITE_COGNITO_CLIENT_ID,
      redirect_uri: appOrigin(),
      response_type: 'code',
      scope: 'openid email profile',
      automaticSilentRenew: true,
      // Tokens stay in the library's default sessionStorage store.
    })
  : null;

// Latest access token, kept in sync so pagehide flushes can send it without awaiting.
let accessToken = null;
userManager?.events.addUserLoaded((user) => {
  accessToken = user.access_token;
});

/** Handles the redirect back from Cognito, then returns the signed-in user or null. */
export async function restoreSession() {
  const params = new URLSearchParams(window.location.search);
  if (params.has('code') && params.has('state')) {
    const user = await userManager.signinRedirectCallback();
    // Return to the page the sign-in started from, without ?code=&state=.
    window.history.replaceState({}, document.title, user.state?.returnTo || '/');
  }
  let user = await userManager.getUser();
  if (user?.expired) {
    try {
      user = await userManager.signinSilent();
    } catch {
      user = null;
    }
  }
  accessToken = user?.access_token ?? null;
  return user;
}

export function signIn() {
  return userManager.signinRedirect({
    state: { returnTo: window.location.pathname + window.location.search },
  });
}

/** Cognito's discovery document has no end_session_endpoint, so logout is a manual redirect. */
export async function signOut() {
  await flushProgress();
  await userManager.removeUser();
  for (const key of Object.keys(localStorage)) {
    if (key.startsWith(PROGRESS_PREFIX)) localStorage.removeItem(key);
  }
  const params = new URLSearchParams({ client_id: env.VITE_COGNITO_CLIENT_ID, logout_uri: appOrigin() });
  window.location.assign(`${env.VITE_COGNITO_DOMAIN}/logout?${params}`);
}

/** fetch with the access token. On a 401 tries one silent refresh, then sends the user to sign in. */
export async function authFetch(url, options = {}) {
  const send = (token) =>
    fetch(url, { ...options, headers: { ...options.headers, Authorization: `Bearer ${token}` } });

  let res = await send(accessToken);
  if (res.status !== 401) return res;

  let user = null;
  try {
    user = await userManager.signinSilent();
  } catch {
    user = null;
  }
  if (!user?.access_token) {
    await signIn();
    throw new Error('Session expired. Redirecting to sign in…');
  }
  accessToken = user.access_token;
  res = await send(accessToken);
  if (res.status === 401) await signIn();
  return res;
}

/** URL of a question file: through the API in cloud mode, the static file locally. */
export function dataUrl(path) {
  return CLOUD ? `/api/data/${path}` : `/${path}`;
}

export function fetchData(path) {
  return CLOUD ? authFetch(dataUrl(path)) : fetch(dataUrl(path));
}

// ---------- Progress sync ----------

const pending = new Map(); // key -> JSON string waiting to be sent
let timer = null;

/**
 * Server copy wins for every key it has; keys only in this browser are uploaded.
 * Runs before the app renders so the synchronous localStorage reads see synced data.
 */
export async function pullProgress() {
  const res = await authFetch('/api/progress');
  if (!res.ok) throw new Error(`Could not load your progress (${res.status})`);
  const { progress } = await res.json();

  for (const [key, value] of Object.entries(progress)) {
    localStorage.setItem(key, JSON.stringify(value));
  }
  for (const key of Object.keys(localStorage)) {
    if (key.startsWith(PROGRESS_PREFIX) && !(key in progress)) {
      pending.set(key, localStorage.getItem(key));
    }
  }
  if (pending.size > 0) schedulePush();
}

/** Queues a save; rapid changes to the same key are sent once. */
export function pushProgress(key, progress) {
  pending.set(key, JSON.stringify(progress));
  schedulePush();
}

function schedulePush() {
  clearTimeout(timer);
  timer = setTimeout(() => {
    flushProgress().catch((err) => console.error('Progress sync failed:', err));
  }, PUSH_DELAY_MS);
}

export async function flushProgress({ keepalive = false } = {}) {
  clearTimeout(timer);
  const batch = [...pending];
  pending.clear();
  const failed = [];

  await Promise.all(
    batch.map(async ([key, body]) => {
      try {
        const options = { method: 'PUT', headers: { 'content-type': 'application/json' }, body, keepalive };
        const res = keepalive
          ? await fetch(`/api/progress/${encodeURIComponent(key)}`, {
              ...options,
              headers: { ...options.headers, Authorization: `Bearer ${accessToken}` },
            })
          : await authFetch(`/api/progress/${encodeURIComponent(key)}`, options);
        if (!res.ok && res.status !== 400) failed.push([key, body]);
      } catch {
        failed.push([key, body]);
      }
    }),
  );

  // Keep failed saves for the next change, unless a newer value was queued meanwhile.
  for (const [key, body] of failed) {
    if (!pending.has(key)) pending.set(key, body);
  }
  if (failed.length > 0 && !keepalive) {
    timer = setTimeout(() => flushProgress().catch(() => {}), 10_000);
  }
}

if (CLOUD) {
  // Send anything still queued when the tab is hidden or closed.
  window.addEventListener('pagehide', () => {
    if (pending.size > 0) flushProgress({ keepalive: true });
  });
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden' && pending.size > 0) flushProgress({ keepalive: true });
  });
}
