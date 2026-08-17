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
- **Applications** — essays, honors, awards, and application progress
- **School Comparison** — compare schools side by side
- **Housing** — dorms, off-campus options, notes
- **Contacts** — admissions reps, counselors, and more
- **Notes** — general notes and reminders

## Workflow

- `main` is always stable.
- New sections/features are built on `feature/<name>` branches and merged once reviewed.
