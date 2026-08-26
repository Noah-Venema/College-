# CollegeOneStop

A personal hub for managing the college search and application process —
scholarships, financial aid, applications, school comparisons, housing, contacts,
notes, a calendar, and a Community space to connect with friends, all in one place.

## Stack
- Flask (backend)
- Flask-SQLAlchemy (SQLite database)
- Flask-Login (authentication)
- Bootstrap 5 (styling)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run (local development)

```bash
python app.py
```

Open http://127.0.0.1:5002 and sign up for an account. Every account gets its own
private set of data across all sections — nothing is shared between users except
what's explicitly posted in the Community tab.

> **Note:** `http://127.0.0.1:5002` is "localhost" — it only ever points to whatever
> computer you open it from. It will **not** work from a different phone or computer
> unless the app is deployed to a public host (see below). This is why the old
> README link couldn't be opened anywhere else.

## Deploying so it works from any device

To get one real URL that works from any computer or phone, deploy to a host with
persistent storage (needed since this app uses a real SQLite file + uploaded
documents). [PythonAnywhere](https://www.pythonanywhere.com) has a free tier that
fits well:

1. Create a free account at pythonanywhere.com.
2. Open a **Bash console** from the dashboard and clone the repo:
   ```bash
   git clone https://github.com/Noah-Venema/College-.git
   cd College-
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. In the **Web** tab, click **Add a new web app** → choose **Manual configuration**
   (Flask) → pick the same Python version as your virtualenv.
4. Set the **virtualenv** path to `/home/<yourusername>/College-/venv`.
5. Edit the generated **WSGI configuration file** so it points at this project's
   `wsgi.py` (already included in the repo), e.g.:
   ```python
   import sys
   path = '/home/<yourusername>/College-'
   if path not in sys.path:
       sys.path.insert(0, path)
   from wsgi import application
   ```
6. On the **Web** tab, add an environment variable `SECRET_KEY` set to a long random
   string (don't reuse the local dev default).
7. Click **Reload** on the Web tab. Your app is now live at
   `https://<yourusername>.pythonanywhere.com` — that's the link to share/bookmark
   instead of the localhost one.

## Sections

- **Home** — dashboard with links to every section
- **Scholarships** — track opportunities, deadlines, and status; a "Discover Scholarships"
  panel links out to real scholarship search sites (Fastweb, Scholarships.com, Bold.org,
  BigFuture, Niche), and each entry can save a real application link with a one-click
  "Apply Now" button
- **Financial Aid** — FAFSA, grants, loans, award letters, and a Cost & Aid Calculator
  that estimates your net cost (with a button to pre-fill aid from your tracked totals)
- **Applications** — essays, honors & awards, activities, school info/transcript, and testing (with file uploads)
- **School Comparison** — compare schools side by side, with matchups and campus notes pulled in
- **Campus** — dorms, food, student-to-teacher ratio, and general campus-life notes per school
- **Contacts** — admissions reps, counselors, and more
- **Notes** — Kanban-style task board (To-Do / In Progress / Done)
- **Calendar** — deadlines with a mini calendar (week/month/year views) and a subscribable `.ics` feed for Google/Apple Calendar
- **Community** — a Reddit/Discord-style space: add friends, and create posts (Public or
  Friends-Only) to discuss your college chances, share your school list, and get feedback,
  with threaded comments

## Workflow

- `main` is always stable.
- New sections/features are built on `feature/<name>` branches and merged once reviewed.

## Roadmap

- Post-secondary/graduate school section (Master's, Doctoral, and other advanced programs)
