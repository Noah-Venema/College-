# CollegeOneStop

A one-stop personal hub for managing the college search and application process —
scholarships, financial aid, applications, school comparisons, housing, contacts,
and notes, all in one place.

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

## Run

```bash
python app.py
```

Open http://127.0.0.1:5002 — on first visit you'll be prompted to create an account
(single-user setup for now).

## Sections

- **Home** — dashboard with links to every section
- **Scholarships** — track opportunities, deadlines, and status
- **Financial Aid** — FAFSA, grants, loans, award letters
- **Applications** — essays, honors & awards, activities, school info/transcript, and testing (with file uploads)
- **School Comparison** — compare schools side by side, with matchups and campus notes pulled in
- **Campus** — dorms, food, student-to-teacher ratio, and general campus-life notes per school
- **Contacts** — admissions reps, counselors, and more
- **Notes** — Kanban-style task board (To-Do / In Progress / Done)
- **Calendar** — deadlines with a mini calendar (week/month/year views) and a subscribable `.ics` feed for Google/Apple Calendar

## Workflow

- `main` is always stable.
- New sections/features are built on `feature/<name>` branches and merged once reviewed.
