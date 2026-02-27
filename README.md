# AloCentra Exam Duty & Timetable Scheduler

AloCentra is an advanced, premium web-based platform designed specifically for the Controller of Examination (COE) and the Exam Cell team of an engineering college. It automates the complex process of exam duty allocation and exam timetable management, saving significant time and reducing manual errors.

## Features

- **Dashboard:** At-a-glance metrics about total faculty, duty sessions, rooms, and upcoming timetables.
- **Rooms Management:** Import and manage exam rooms and their capacities via Excel.
- **Faculty Management:** Manage faculty members, departments, and designations. Import via Excel and assign them roles.
- **Duty Assignment Wizard:** A dynamic engine to intelligently allocate invigilators and relievers based on specified duty targets, skipping Sundays, and printing the results.
- **Exam Timetable Builder:** Interactive grid builder to quickly assign subjects and courses to specific dates, making it drastically easier for the COE to finalize timetables.
- **User Role Management:** An invite-based system powered by Celery tasks, allowing the COE to delegate specific permissions to Exam Cell staff seamlessly.

## Tech Stack

- **Backend:** Django 5, PostgreSQL
- **Frontend:** Vanilla JS, Bootstrap 5, Custom CSS Variables for styling.
- **Async Processing:** Celery + Redis for email dispatches.
- **Hosting / Deploy:** Docker & Docker Compose setup included.

## Quick Start (Docker)

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill the variables.
3. Run `docker-compose up -d --build`
4. Access the server at `http://localhost:8000`

See `SETUP_GUIDE.md` for manual, local setup instructions.
