# 🏥 LifeCare Clinic – Clinic Management System

> A full-featured, production-ready clinic management web application built with Python Flask.

---

## 🌐 Live URL
- **Local Dev:** http://localhost:5000
- **Admin Login:** `admin@lifecareclinic.com` / `Admin@123456`

---

## ✨ Features

### Public Pages
| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Hero, stats counter, featured doctors, CTA |
| About | `/about` | Clinic story, mission, values |
| Services | `/services` | All medical specializations |
| Doctors | `/doctors` | All active specialist doctors |
| Contact | `/contact` | Contact form, address, working hours |

### Patient Portal
| Feature | URL | Description |
|---------|-----|-------------|
| Register | `/auth/register` | Email + phone + password registration |
| OTP Verify | `/auth/verify-otp` | 6-digit email OTP verification |
| Login | `/auth/login` | Secure session-based login |
| Dashboard | `/patient/dashboard` | Stats, upcoming appointments |
| Book Appointment | `/patient/book-appointment` | Select doctor → date → time slot |
| My Appointments | `/patient/my-appointments` | View, filter, cancel appointments |
| Profile | `/patient/profile` | Update personal info & password |

### Admin Panel
| Feature | URL | Description |
|---------|-----|-------------|
| Admin Dashboard | `/admin/dashboard` | Stats: patients, doctors, appointments |
| Manage Patients | `/admin/patients` | View/search/delete patients |
| Manage Doctors | `/admin/doctors` | Add/Edit/Deactivate doctors |
| Add Doctor | `/admin/doctors/add` | Full doctor profile form |
| Edit Doctor | `/admin/doctors/edit/<id>` | Update doctor details |
| Manage Appointments | `/admin/appointments` | View, approve, cancel appointments |

---

## 🗄️ Database Schema

### `users`
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| name | String(120) | Full name |
| email | String(150) UNIQUE | Email address |
| phone | String(15) | Mobile number |
| password | String(256) | Bcrypt hashed |
| role | String(20) | `patient` or `admin` |
| is_verified | Boolean | Email OTP verified |
| gender | String(10) | Male/Female/Other |
| dob | Date | Date of birth |
| address | Text | Full address |
| blood_group | String(5) | A+, B-, etc. |

### `doctors`
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| name | String(120) | Doctor name |
| specialization | String(100) | Medical specialty |
| qualification | String(200) | Degrees |
| experience | Integer | Years |
| fee | Float | Consultation fee |
| available_days | String | Comma-separated |
| available_slots | String | Comma-separated time slots |
| rating | Float | 0.0 – 5.0 |
| is_active | Boolean | Show to patients |

### `appointments`
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| patient_id | FK → users | Patient reference |
| doctor_id | FK → doctors | Doctor reference |
| date | Date | Appointment date |
| time_slot | String(20) | e.g. "10:00" |
| status | String(20) | pending/approved/cancelled |
| symptoms | Text | Patient description |
| notes | Text | Doctor/admin notes |

### `otps`
| Column | Type | Description |
|--------|------|-------------|
| email | String(150) | User email |
| otp_code | String(6) | 6-digit code |
| is_used | Boolean | Consumed flag |
| expires_at | DateTime | TTL: 10 minutes |

---

## 🚀 Quick Start

```bash
# 1. Clone the project
git clone <repo-url>
cd webapp

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your SMTP credentials

# 5. Initialize database & seed doctors
python seed_doctors.py

# 6. Run the application
python run.py
```

---

## ⚙️ Environment Configuration (`.env`)

```env
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///bajrang_clinic.db

# Gmail SMTP (create App Password in Google Account)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Admin Account
ADMIN_EMAIL=admin@lifecareclinic.com
ADMIN_PASSWORD=Admin@123456
```

---

## 🌐 PythonAnywhere Deployment

1. Upload project to PythonAnywhere
2. Create virtualenv and install requirements
3. Configure WSGI file to point to `wsgi.py`
4. Set environment variables in the `.env` file
5. Set `DEBUG=False` in production

```python
# WSGI config (PythonAnywhere)
import sys
sys.path.insert(0, '/home/yourusername/webapp')
from wsgi import application
```

---

## 🎨 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python Flask 3.x |
| Database | SQLite (SQLAlchemy ORM) |
| Auth | Flask-Login + Werkzeug hashing |
| Email | Flask-Mail (Gmail SMTP) |
| Security | Flask-WTF CSRF protection |
| Frontend | HTML5 + Bootstrap 5 + Custom CSS |
| Icons | Font Awesome 6 |
| JS | Vanilla JS (no frameworks) |
| Fonts | Google Fonts (Poppins) |

---

## 🛡️ Security Features

- ✅ Password hashing with Werkzeug (PBKDF2 SHA-256)
- ✅ CSRF protection on all forms
- ✅ Session-based authentication
- ✅ Role-based access control (admin/patient)
- ✅ Email OTP verification (10 min expiry, single-use)
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ XSS prevention via Jinja2 auto-escaping
- ✅ HTTP-only session cookies

---

## 📁 Project Structure

```
webapp/
├── __init__.py          # App factory
├── run.py               # Dev server entry
├── wsgi.py              # Production WSGI
├── seed_doctors.py      # Sample data
├── requirements.txt
├── .env                 # Environment variables
├── .gitignore
├── models/
│   ├── user.py          # User/Patient model
│   ├── doctor.py        # Doctor model
│   ├── appointment.py   # Appointment model
│   └── otp.py           # OTP model
├── routes/
│   ├── public.py        # Public pages
│   ├── auth.py          # Login/Register/OTP
│   ├── patient.py       # Patient portal
│   └── admin.py         # Admin panel
├── utils/
│   ├── email.py         # OTP email sending
│   └── decorators.py    # Auth decorators
├── templates/
│   ├── base.html        # Public base template
│   ├── public/          # Home, About, Services, etc.
│   ├── patient/         # Patient portal templates
│   └── admin/           # Admin panel templates
└── static/
    ├── css/style.css    # Main stylesheet (~44KB)
    └── js/main.js       # Main JavaScript (~20KB)
```

---

## 🔑 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@lifecareclinic.com | Admin@123456 |
| Patient | Register via /auth/register | Your chosen password |

---

*© 2024 LifeCare Clinic. Built with ❤️ for better healthcare.*
