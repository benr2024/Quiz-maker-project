# Quiz Classroom

A desktop application designed to facilitate classroom testing and student tracking. The user interface styling and colour schemes were designed using Replit AI, whilst all functional backend logic—including SQLite database management, authentication, navigation, quiz creation, test-taking, and Matplotlib analytics—was programmed independently.

---

## Key Features

### For Students
* **Account Registration & Login:** Register under a specific teacher and receive an auto-generated Student ID (e.g., `S0001`).
* **Interactive Quizzes:** View available subject tests created by their assigned teacher.
* **Instant Feedback & Scoring:** Navigate questions, submit answers, and receive detailed test results showing correct answers and total score percentage.
* **Progress Tracking:** Graph quiz performance percentage over time.

### For Teachers
* **Account Registration & Login:** Register to receive an auto-generated Teacher ID (e.g., `T0001`).
* **Quiz Builder:** Create quizzes for various subjects with up to 10 custom questions and answer keys.
* **Student Management:** View registered students, reset student passwords, reassign students to different teachers, or remove student accounts.
* **Analytics:** View performance graphs for individual students to monitor their progress across completed tests.

---

## Database Architecture

The application uses an **SQLite3** local database (`micro.db`) containing six relational tables:

| Table Name | Description | Key Fields |
| :--- | :--- | :--- |
| **`teacher`** | Stores teacher credentials | `teacher_id`, `teacher_first_name`, `teacher_surname`, `password` |
| **`student`** | Stores student accounts linked to a teacher | `student_id`, `teacher_id`, `student_first_name`, `student_surname`, `password` |
| **`subject`** | Maps subjects to unique IDs | `subject_id`, `subject_name` |
| **`test`** | Links quizzes to subjects and teachers | `test_id`, `subject_id`, `teacher_id` |
| **`questions`** | Holds individual questions and answer keys for tests | `question_id`, `test_id`, `question`, `answer` |
| **`score`** | Stores student test results and percentages | `test_id`, `student_id`, `score` |

---

## Technical Stack & Dependencies

* **Python 3**
* **Tkinter:** Graphical User Interface (GUI) components
* **SQLite3:** Relational database management
* **Matplotlib & NumPy:** Data visualisation for student progress tracking

---

## Getting Started

### Prerequisites

Ensure Python 3 is installed along with `matplotlib` and `numpy`:

```bash
pip install matplotlib numpy

### Installation & Execution

1. Clone or download the repository.
2. Run the main script file:

```bash
python quizproject.py
