Here's a well-structured `README.md` content for your **Quiz-master** project, formatted in Markdown:

---

# 📚 Quiz-master

**Quiz-master** is a web-based quiz platform designed for seamless quiz creation, management, and user interaction. It allows **admins** to create subject- and chapter-wise quizzes, while **users** can attempt quizzes, track their scores, and review past attempts. Admins have control over user access and quiz approvals.

---

## 🚀 Features

- User registration and login with admin approval.
- Admin dashboard to manage quizzes, users, and content.
- Quiz creation categorized by **subjects** and **chapters**.
- Timed quizzes with auto-submission.
- Dynamic quiz interface with real-time countdown.
- Users can view results and quiz history.
- Role-based access and session management.
- Scheduler for real-time quiz status updates.

---

## 🧰 Technologies Used

- **Flask** – Backend web framework.
- **Jinja2** – Templating engine for HTML rendering.
- **SQLite** – Lightweight relational database.
- **Flask-Login** – Authentication and session handling.
- **CSS** – Internal CSS for basic styling.
- **JavaScript** – For quiz timers and dynamic behavior.

---

## 🗃️ Database Schema

### 🔐 Admin Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `name` | String(100) | Admin name |
| `email` | String(120) | Unique email |
| `password` | String(255) | Hashed password |

### 👤 User Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `name` | String(100) | User name |
| `email` | String(120) | Unique email |
| `password` | String(255) | Hashed password |
| `qualification` | String(100) | Optional qualification |
| `dob` | Date | Date of birth |
| `allow` | Boolean | Admin-controlled access |

### 📘 Subject Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `name` | String(100) | Subject name |
| `description` | Text | Subject description |

### 📗 Chapter Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `name` | String(100) | Chapter name |
| `description` | Text | Chapter description |
| `subject_id` | Integer | Foreign Key to `Subject.id` |

### 📝 Quiz Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `name` | String(100) | Quiz title |
| `description` | Text | Quiz details |
| `create_date` | DateTime | Created timestamp |
| `startline` | DateTime | Start time |
| `total_score` | Integer | Max score |
| `duration` | Integer | Duration in minutes |
| `deadline` | DateTime | Last access time |
| `status` | String(50) | Draft / Published |
| `approved` | Boolean | Approved for users |
| `chapter_id` | Integer | Foreign Key to `Chapter.id` |

### ❓ Questions Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `index` | Integer | Question number |
| `text` | Text | Question content |
| `quiz_id` | Integer | Foreign Key to `Quiz.id` |
| `option1-4` | String(255) | Answer options |
| `correct_option` | Integer | Correct option index |
| `marks` | Integer | Points awarded |

### 📊 Scores Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `user_id` | Integer | Foreign Key to `User.id` |
| `quiz_id` | Integer | Foreign Key to `Quiz.id` |
| `score` | Integer | User score (out of 100) |
| `status` | String(50) | Attempt status |

### ✅ UserAnswer Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary Key |
| `user_id` | Integer | Foreign Key to `User.id` |
| `quiz_id` | Integer | Foreign Key to `Quiz.id` |
| `selected_answer` | String(255) | Stored answers |
| `score` | Integer | Score for attempt |

---

## 🧱 Architecture

The application follows the **MVC (Model-View-Controller)** architecture:

- **Controllers**: Flask routes handle quiz logic, session, and API endpoints.
- **Models**: ORM-backed classes define and interact with the SQLite schema.
- **Views**: HTML templates powered by Jinja2, styled with internal CSS, and dynamic using JavaScript (e.g., `setInterval()` for countdown timer).

### 🕒 Scheduler
A time-based job scheduler (e.g., using `APScheduler` or `Flask-Cron`) updates quiz statuses based on UTC timestamps.

---

## 🛠️ Setup & Installation (Optional section)
```bash
git clone https://github.com/yourusername/quiz-master.git
cd quiz-master
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## 📬 Contact

For queries or contributions, reach out via [dutondeyash21@gmail.com or YashD2109].


