# College Admission and Student Enrollment Management System

A production-quality full-stack web application built with **Python 3** and **Django**, designed with a modern academic portal UI/UX architecture. Suitable for BCA / Computer Applications academic project evaluations and real-world institution admissions workflows.

---

## 🌟 Key Highlights & Design Fidelity
- **Unified Academic Portal Theme:** Built with Deep Navy Blue (`#0B3A6E`), Sidebar Navy (`#07264a`), and Action Blue (`#1677FF`) with rounded cards, soft shadows, and responsive layout.
- **Role-Based Access Control (RBAC):** Strict view-level authorization enforcing role separation between `STUDENT` and `ADMIN`.
- **Multi-Step Application Wizard:** 5-step stepper (Personal Details, Academic Records, Course Preference, Document Uploads, Review & Submit) with draft resume capability.
- **Seat Capacity Tracking:** Automated real-time seat reservation and decrementation upon enrollment confirmation; prevents overselling and duplicate admissions.
- **Printable / Downloadable Enrollment Letter:** Formal institutional letterhead with official seal, student roll number, reference ID, and registrar sign-off lines.
- **Document Verification Queue:** Scanned certificate upload with file type/size validation, and administrative verification or rejection with specified reasons.
- **In-App Notifications:** Real-time notifications for status changes, verification updates, and badge count in the top navigation bar.
- **Admin Analytics & CSV Exports:** Interactive monthly application trend chart, seat occupancy matrix, and downloadable CSV reports.
- **Automated Test Suite:** 19 automated test cases covering authentication, CRUD, permissions, seat counting, and document verification.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Git (optional)

### 2. Setup Virtual Environment (Optional but recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Seed Realistic Demo Data
Populates the database with realistic programs, applications, documents, and credentials:
```bash
python manage.py seed_data
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

Open your browser and visit:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@college.edu` | `admin123` | Full administrative control, approvals, reports |
| **Demo Student** | `rahul@gmail.com` | `student123` | Pre-populated applicant (Matches reference design) |
| **Demo Student 2** | `nihal@gmail.com` | `student123` | Applicant with pending application |
| **New Student** | Self-register | Any password | Public registration portal at `/register/` |

> 💡 *Tip: The login page includes quick one-click autofill buttons for both Admin and Student demo credentials.*

---

## 🏗️ Project Architecture

```text
admissioan/
│
├── config/                  # Django project configuration
│   ├── settings.py          # Unified settings & app configurations
│   ├── urls.py              # Central routing & media serving
│   ├── wsgi.py              # WSGI entrypoint
│   └── views.py             # Custom 404, 403, 500 error handlers
│
├── accounts/                # Custom User model, authentication, RBAC
│   ├── models.py            # User model (Student vs Admin roles)
│   ├── forms.py             # Registration, Login, and Settings forms
│   ├── views.py             # Auth flows, landing page, Admin Dashboard
│   ├── backends.py          # Dual email/username authentication backend
│   ├── decorators.py        # @student_required and @admin_required
│   └── management/commands/ # seed_data command for realistic demo data
│
├── students/                # Student profiles & Admin student management
│   ├── models.py            # StudentProfile (Personal, Guardian, Academic)
│   └── views.py             # Student dashboard, profile edit, admin search
│
├── courses/                 # Degree programs & seat matrix
│   ├── models.py            # Course model with seat decrement/restore logic
│   ├── forms.py             # CourseForm with validation
│   └── views.py             # Course management, student catalog, JSON API
│
├── admissions/              # 5-Step Admission application flow
│   ├── models.py            # AdmissionApplication & ApplicationTimeline
│   ├── forms.py             # Step forms and admin review forms
│   └── views.py             # Application wizard, review queues, audit logs
│
├── enrollments/             # Final seat confirmation & enrollment letters
│   ├── models.py            # Enrollment model with automated roll numbering
│   └── views.py             # Confirmation view, letter generation, admin roster
│
├── documents/               # File uploads & verification queue
│   ├── models.py            # Document model with verification statuses
│   ├── forms.py             # Secure upload form with size/type validation
│   └── views.py             # Student document vault, admin verification modal
│
├── notifications/           # In-app alerts & navbar badge counter
│   ├── models.py            # Notification model
│   ├── services.py          # send_notification helper
│   ├── context_processors.py# Global unread count & recent dropdown items
│   └── views.py             # Notifications list and mark-as-read endpoints
│
├── reports/                 # Administrative metrics & exports
│   └── views.py             # Breakdown statistics, seat matrix, CSV exports
│
├── static/                  # Design assets
│   ├── css/style.css        # Clean custom design system
│   └── js/main.js           # Password toggles, responsive sidebar, charts
│
├── templates/               # Modular Django templates
│   ├── base.html            # Master layout with navbar, sidebar, alerts
│   ├── accounts/            # Home, login, register, admin dashboard, settings
│   ├── students/            # Student dashboard, profile, admin student views
│   ├── courses/             # Course catalog and course management
│   ├── admissions/          # Application stepper, status views, review pages
│   ├── enrollments/         # Confirmation screen, formal letter, roster
│   ├── documents/           # Document upload & verification queue
│   ├── notifications/       # User notification center
│   ├── reports/             # System reports overview
│   └── errors/              # Custom 404, 403, and 500 error templates
│
└── requirements.txt         # Project dependencies
```

---

## 🧪 Running the Automated Test Suite

To run all 19 test cases:
```bash
python manage.py test
```

Expected output:
```text
Creating test database for alias 'default'...
...................
----------------------------------------------------------------------
Ran 19 tests in 23.529s

OK
Destroying test database for alias 'default'...
```

---

## 🛡️ Security Features
- **Backend-enforced CSRF protection** on all forms.
- **PBKDF2 Password Hashing** through Django authentication.
- **View-Level Permissions** preventing privilege escalation (students attempting to access admin endpoints are blocked).
- **Secure File Validation** (5MB maximum size restriction, allowed extensions: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.webp`).
- **SQL Injection Prevention** through Django ORM parameterized queries.
- **Custom Error Pages (404, 403, 500)** to prevent technical stack trace exposure.

---

## 🎓 Academic Project Evaluation Checklist
- [x] Full-stack architecture using Python & Django.
- [x] Non-trivial relational database models with foreign keys, unique constraints, and timestamps.
- [x] Multi-step application wizard with state persistence.
- [x] Exact aesthetic match to the modern college portal reference design.
- [x] Seed data command for instant evaluation readiness.
- [x] 100% test coverage on critical business workflows.

---

## ☁️ Deploying to Vercel

This repository is pre-configured for seamless deployment to **Vercel** serverless functions with **WhiteNoise** static asset compression.

### 1. Push Project to GitHub
```bash
git add .
git commit -m "Deploy: College Admission and Student Enrollment Management System"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### 2. Import into Vercel
1. Go to [vercel.com](https://vercel.com/) and sign in with your GitHub account.
2. Click **"Add New..."** > **"Project"**.
3. Import your GitHub repository (`college-admission-portal` or your chosen repo name).
4. In **Project Settings**:
   - Framework Preset: **Other**
   - Root Directory: `./` (leave default)
5. Under **Environment Variables**, add:
   - `SECRET_KEY`: (A strong random secret key string)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.vercel.app`
   - `DATABASE_URL`: *(Recommended for production)* A PostgreSQL connection string from Neon, Supabase, or AWS RDS (e.g. `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`).
6. Click **Deploy**. Vercel will build the Python WSGI serverless function and publish your site!

