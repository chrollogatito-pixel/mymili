# Deploying this project to Netlify (static export)

This repository contains a small Django app and a management command that can render the main views and gather static files into a `dist/` directory suitable for Netlify.

Quick summary:

- We added `amor/management/commands/export_static.py` which:
  - Renders the app's pages (`/`, `/playlists/`, `/diary/`, `/proposal/`) into HTML files inside `dist/`.
  - Runs `collectstatic` and copies static files into `dist/static/`.

- `requirements.txt` lists `Django==5.2.5`.
- `netlify.toml` is included and contains the build command and publish directory.

Local build (recommended to test before Netlify):

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies and generate `dist/` (run from repo root):

```powershell
pip install -r requirements.txt
python mimili/manage.py export_static -o dist
```

3. Serve the `dist/` folder locally to verify (optional):

```powershell
# from repo root
python -m http.server 9000 --directory .\dist
# open http://localhost:9000
```

Netlify setup options

- Quick manual: run the local export and drag & drop `dist/` into Netlify's Sites dashboard.

- CI-style (recommended): connect your repository to Netlify and use these settings:
  - Build command:

    python -m pip install -r requirements.txt && python mimili/manage.py export_static -o dist

  - Publish directory: `dist`

Netlify build notes and tips

- Make sure `requirements.txt` is at the repository root (it is).
- If you need a specific Python version, add a `runtime.txt` or set the `PYTHON_VERSION` in Netlify's Build Environment settings.
- The static export is fully static: any view that requires database writes, sessions or user auth won't work as dynamic endpoints on Netlify.

If you'd like, I can:

- Auto-detect `urlpatterns` and export all public GET routes instead of the small hard-coded list.
- Add a `runtime.txt` with a pinned Python version.
- Add a `_headers` or `_redirects` file for SPA routing or caching headers.

Done in this repo:

- `runtime.txt` (requests Python 3.11 on Netlify build image).
- The `export_static` command now writes a basic `_redirects` into `dist/` so routes fallback to `index.html` (useful for SPA-like behavior).

Tell me if you want `_headers` or more advanced redirect rules added.

Firebase realtime integration (optional)

I added a tiny Firebase Realtime Database demo to `dist/index.html`. It's disabled until you put your Firebase config in place. Steps to enable:

1. Create a Firebase project at https://console.firebase.google.com/ and add a Web app.
2. In the Firebase Console, go to Realtime Database → Create database → Start in locked mode (you can set rules to allow test writes while developing).
3. Copy the Firebase config object and replace the placeholders in `dist/index.html` (`REPLACE_API_KEY`, `REPLACE_PROJECT`, etc.).
4. (Optional) Update Realtime Database rules to allow writes from authenticated users, or keep public rules for quick testing:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

5. Open `dist/index.html` in a browser (or deploy to Netlify). The small chat widget will connect to the `public_messages` path and show new messages in real time.

Security note: For production you should secure writes with Firebase Authentication and stricter DB rules. I can add an authenticated flow or server-side Netlify Function to publish messages if you want.