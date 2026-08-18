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

## Run

```bash
python app.py
```

Open http://127.0.0.1:5002 and sign up for an account. Every account gets its own
private set of data across all sections — nothing is shared between users except
what's explicitly posted in the Community tab.

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
