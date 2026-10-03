from tkinter import *
import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import DISABLED
import random
import matplotlib.pyplot as plt
import numpy as np


# A warm, high-contrast classroom palette: paper, deep teal, and a small
# ochre accent. All styling stays within Tkinter so the app remains lightweight.
COLORS = {
    "paper": "#F3F2E9",
    "surface": "#FFFDF7",
    "ink": "#20383D",
    "muted": "#687B79",
    "teal": "#276B68",
    "teal_active": "#1D5957",
    "teal_pale": "#DCEAE5",
    "ochre": "#C18A43",
    "line": "#D7DED5",
    "danger": "#A44E48",
}


def configure_classroom_style(app):
    """Set native Tk defaults once, including for widgets created later."""
    app.configure(background=COLORS["paper"])
    app.option_add("*Background", COLORS["paper"])
    app.option_add("*Foreground", COLORS["ink"])
    app.option_add("*Font", ("TkDefaultFont", 11))
    app.option_add("*Label.Background", COLORS["paper"])
    app.option_add("*Label.Foreground", COLORS["ink"])
    app.option_add("*Button.Background", COLORS["surface"])
    app.option_add("*Button.Foreground", COLORS["ink"])
    app.option_add("*Button.ActiveBackground", COLORS["teal_pale"])
    app.option_add("*Button.ActiveForeground", COLORS["ink"])
    app.option_add("*Button.Relief", "flat")
    app.option_add("*Button.BorderWidth", 0)
    app.option_add("*Button.Padx", 16)
    app.option_add("*Button.Pady", 9)
    app.option_add("*Entry.Background", COLORS["surface"])
    app.option_add("*Entry.Foreground", COLORS["ink"])
    app.option_add("*Entry.InsertBackground", COLORS["teal"])
    app.option_add("*Entry.Relief", "flat")
    app.option_add("*Entry.HighlightThickness", 1)
    app.option_add("*Entry.HighlightBackground", COLORS["line"])
    app.option_add("*Entry.HighlightColor", COLORS["teal"])
    app.option_add("*OptionMenu.Background", COLORS["surface"])
    app.option_add("*OptionMenu.Relief", "flat")
    app.option_add("*Menu.Background", COLORS["surface"])
    app.option_add("*Menu.Foreground", COLORS["ink"])
    app.option_add("*Menu.ActiveBackground", COLORS["teal_pale"])
    app.option_add("*Menu.ActiveForeground", COLORS["ink"])


PAGE_COPY = {
    "LoginMenu": ("Sign in", "Pick up where your class left off."),
    "RegisterMenu": ("Create an account", "A place for every learner and teacher."),
    "StudentFirstMenu": ("Your learning space", "Choose what you would like to work on."),
    "MyProgress": ("Your progress", "A little practice adds up."),
    "MyQuizzes": ("Available quizzes", "Choose a subject to begin."),
    "TeacherFirstMenu": ("Teacher workspace", "Build a quiz or check in with your students."),
    "MyStudentsMenu": ("Your students", "Manage learners and follow their progress."),
    "CreateQuizMenu": ("Build a quiz", "Add a subject, then write up to ten questions."),
}


def style_screen(frame):
    """Apply a consistent page shell and gently tune native widgets."""
    frame.configure(background=COLORS["paper"])
    page = PAGE_COPY.get(frame.__class__.__name__)
    if page and not getattr(frame, "_classroom_header", None):
        header = tk.Frame(frame, bg=COLORS["paper"])
        tk.Label(
            header, text="QUIZ  /  CLASSROOM", bg=COLORS["paper"],
            fg=COLORS["teal"], font=("TkDefaultFont", 9, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header, text=page[0], bg=COLORS["paper"], fg=COLORS["ink"],
            font=("Georgia", 23, "bold"),
        ).pack(anchor="w", pady=(5, 0))
        tk.Label(
            header, text=page[1], bg=COLORS["paper"], fg=COLORS["muted"],
            font=("TkDefaultFont", 10),
        ).pack(anchor="w", pady=(2, 0))
        tk.Frame(header, bg=COLORS["ochre"], height=2).pack(fill="x", pady=(13, 0))
        first = frame.winfo_children()[0] if frame.winfo_children() else None
        header.pack(fill="x", padx=36, pady=(25, 8), before=first)
        frame._classroom_header = header
    elif page:
        header = frame._classroom_header
        if not header.winfo_manager():
            first = next((w for w in frame.winfo_children() if w is not header), None)
            header.pack(fill="x", padx=36, pady=(25, 8), before=first)

    def visit(widget):
        # Keep deliberately chosen fills (hero panels, accent rules, and action
        # buttons) intact; the option database already supplies defaults.
        if isinstance(widget, tk.Label):
            try:
                widget.pack_configure(padx=12, pady=5)
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Button):
            try:
                text = str(widget.cget("text")).strip().lower()
                danger = text.startswith("delete")
                primary = text in {
                    "login", "register", "create quiz", "my quizzes",
                    "my progress", "view progress", "set password", "confirm",
                    "submit", "finish test", "create test", "show progress graph",
                    "back to menu",
                }
                widget.configure(
                    background=COLORS["danger"] if danger else (
                        COLORS["teal"] if primary else COLORS["surface"]
                    ),
                    foreground=COLORS["surface"] if primary or danger else COLORS["ink"],
                    activebackground=COLORS["teal_active"] if primary else COLORS["teal_pale"],
                    activeforeground=COLORS["surface"] if primary or danger else COLORS["ink"],
                    cursor="hand2",
                    font=("TkDefaultFont", 10, "bold" if primary or danger else "normal"),
                )
                widget.pack_configure(padx=10, pady=6)
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Entry):
            try:
                widget.configure(width=34, font=("TkDefaultFont", 11), insertwidth=2)
                widget.pack_configure(padx=12, pady=6)
            except tk.TclError:
                pass
        elif isinstance(widget, tk.OptionMenu):
            try:
                widget.configure(
                    background=COLORS["surface"], foreground=COLORS["ink"],
                    activebackground=COLORS["teal_pale"], cursor="hand2",
                )
                widget.pack_configure(padx=12, pady=7)
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Frame):
            try:
                widget.configure(background=COLORS["paper"])
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            visit(child)

    visit(frame)



def check_if_quiz_completed(student_id):
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT score FROM score WHERE student_id = ?", (student_id,))
        result = cursor.fetchall()
        if result:
            return print([row[0] for row in result])


#check_if_quiz_completed('S0001')

def show_test_and_questions():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()

        # Fetch all tests
        cursor.execute("SELECT * FROM test")
        tests = cursor.fetchall()

        if not tests:
            print("No tests found.")
        else:
            print("\n--- Tests Table ---")
            print("test_id | subject_id | teacher_id")
            for test in tests:
                print(test)

        # Fetch all questions
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()

        if not questions:
            print("\nNo questions found.")
        else:
            print("\n--- Questions Table ---")
            print("question_id | test_id | question | answer")
            for question in questions:
                print(question)

# Call the function to display the data
#show_test_and_questions()



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Classroom")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(960, max(560, screen_width - 48))
        window_height = min(740, max(500, screen_height - 64))
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(min(680, window_width), min(560, window_height))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        configure_classroom_style(self)

        self.current_teacher_id = None
        self.current_student_id = None

        # Create frames for different pages
        self.menu_frame = FirstMenu(self)
        self.login_frame = LoginMenu(self)
        self.register_frame = RegisterMenu(self)
        self.teacher_frame = TeacherFirstMenu(self)
        self.create_quiz_frame = CreateQuizMenu(self)
        self.my_students_frame = MyStudentsMenu(self)
        self.student_frame = StudentFirstMenu(self)
        self.my_quizzes_frame = MyQuizzes(self)
        self.my_progress_frame = MyProgress(self)

        # Show the menu initially
        self.show_frame(self.menu_frame)

    def show_frame(self, frame):
        if isinstance(frame, CreateQuizMenu):
            frame.reset()
        elif isinstance(frame, MyStudentsMenu):
            frame.show_students()
        elif isinstance(frame, MyQuizzes):
            frame.reset()

        elif isinstance(frame, MyProgress):
            frame.show_graph()
        style_screen(frame)
        frame.grid(row=0, column=0, sticky="nesw")
        frame.tkraise()


class FirstMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["paper"])
        self.grid(row=0, column=0, sticky="nesw")
        hero = tk.Frame(self, bg=COLORS["paper"])
        hero.pack(expand=True, fill="both", padx=48, pady=34)
        tk.Label(
            hero, text="QUIZ  /  CLASSROOM", bg=COLORS["paper"],
            fg=COLORS["teal"], font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor="w", pady=(16, 12))
        tk.Label(
            hero, text="A good place\nto work it out.", bg=COLORS["paper"],
            fg=COLORS["ink"], justify="left", font=("Georgia", 34, "bold"),
        ).pack(anchor="w")
        tk.Label(
            hero, text="Practice, teach, and keep track of the little wins.",
            bg=COLORS["paper"], fg=COLORS["muted"], font=("TkDefaultFont", 12),
        ).pack(anchor="w", pady=(12, 28))
        accent = tk.Frame(hero, bg=COLORS["ochre"], height=3)
        accent.pack(fill="x", pady=(0, 26))
        login_button = tk.Button(
            hero, text="Login", command=lambda: parent.show_frame(parent.login_frame),
            width=24, font=("TkDefaultFont", 11, "bold"),
        )
        login_button.pack(anchor="w", pady=(0, 10), ipady=5)
        register_button = tk.Button(
            hero, text="Register", command=lambda: parent.show_frame(parent.register_frame),
            width=24, font=("TkDefaultFont", 11, "bold"),
        )
        register_button.pack(anchor="w", ipady=5)
        tk.Label(
            hero, text="For students and teachers", bg=COLORS["paper"],
            fg=COLORS["muted"], font=("TkDefaultFont", 9),
        ).pack(anchor="w", pady=(34, 0))


class LoginMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid(row=0, column=0, sticky="nesw")

        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.menu_frame))
        back_button.pack(pady=10)

        tk.Label(self, text="Your account details", fg=COLORS["muted"]).pack(pady=10)

        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        login_button = tk.Button(self, text="Login", command=self.login)
        login_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if check_username(username) == False:
            messagebox.showerror("Error", "Username not found")
            return
        elif check_password(username, password) == False:
            messagebox.showerror("Error", "Incorrect password")
            return
        else:
            messagebox.showinfo("Success", "Login successful")
            if username[0] == "T":
                self.master.current_teacher_id = username
                self.master.show_frame(self.master.teacher_frame)
            else:
                self.master.current_student_id = username
                self.master.show_frame(self.master.student_frame)


class RegisterMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nesw")

        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.menu_frame))
        back_button.pack(pady=10)

        student_or_teacher = ['Student', 'Teacher']
        self.selected_student_or_teacher = tk.StringVar()
        self.selected_student_or_teacher.set(student_or_teacher[0])

        dropdown = tk.OptionMenu(self, self.selected_student_or_teacher, *student_or_teacher)
        dropdown.pack()

        self.selected_student_or_teacher.trace("w", self.option_choice)

        tk.Label(self, text="First Name:").pack()
        self.first_name_entry = tk.Entry(self)
        self.first_name_entry.pack()

        tk.Label(self, text="Last Name:").pack()
        self.last_name_entry = tk.Entry(self)
        self.last_name_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self)
        self.password_entry.pack()

        self.teacher_label = tk.Label(self, text="Enter your teacher's last name:")
        self.teacher_entry = tk.Entry(self)

        self.option_choice()

        register_button = tk.Button(self, text="Register", command=self.register)
        register_button.pack()

    def option_choice(self, *args):
        if self.selected_student_or_teacher.get().upper() == "STUDENT":
            self.teacher_label.pack()
            self.teacher_entry.pack()
        else:
            self.teacher_label.pack_forget()
            self.teacher_entry.pack_forget()

    def register(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        password = self.password_entry.get()

        if first_name.strip() == "" or last_name.strip() == "" or password.strip() == "":
            messagebox.showerror("Error, Please fill in all fields")
            return

        if self.selected_student_or_teacher.get().upper() == "STUDENT":
            teacher_last_name = self.teacher_entry.get()
            with sqlite3.connect("micro.db") as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM teacher WHERE teacher_surname = ?", (teacher_last_name,))
                teacher = cursor.fetchone()
            if teacher is None:
                messagebox.showerror("Error, The teacher is not found")

            elif teacher_last_name == "":
                messagebox.showerror("Error, Please fill in all fields")

            else:
                teacher_id = teacher[0]
                student_id = generate_new_id(self.selected_student_or_teacher.get().upper())
                with sqlite3.connect("micro.db") as db:
                    cursor = db.cursor()
                    cursor.execute(
                        "INSERT INTO student(student_id,teacher_id, student_first_name,student_surname,password) VALUES(?,?,?,?,?)",
                        (student_id, teacher_id, first_name, last_name, password))
                    db.commit()

                messagebox.showinfo("Successfully registered", f"Your student ID is: {student_id}")
                self.master.show_frame(self.master.menu_frame)

        else:
            teacher_id = generate_new_id(self.selected_student_or_teacher.get().upper())
            with sqlite3.connect("micro.db") as db:
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO teacher(teacher_id,teacher_first_name,teacher_surname,password) VALUES(?,?,?,?)",
                    (teacher_id, first_name, last_name, password))
                db.commit()
            messagebox.showinfo("Successfully registered", f"Your Teacher ID is: {teacher_id}")
            self.master.show_frame(self.master.menu_frame)



class StudentFirstMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nesw")

        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.student_frame))
        back_button.pack(pady=10)

        my_quizzes_button = tk.Button(self, text="My Quizzes", command=lambda: parent.show_frame(parent.my_quizzes_frame))
        my_quizzes_button.pack()

        my_progress_button = tk.Button(self, text="My Progress", command=lambda: parent.show_frame(parent.my_progress_frame))
        my_progress_button.pack()

class MyProgress(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nesw")

        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.student_frame))
        back_button.pack(pady=10)
        
        # Add a button to show the graph
        self.show_graph_button = tk.Button(self, text="Show Progress Graph", command=self.display_graph)
        self.show_graph_button.pack(pady=20)
        
        # Create a label to show information
        self.info_label = tk.Label(self, text="Click the button above to view your progress graph.\nClose the graph window to return here.")
        self.info_label.pack(pady=10)

    def show_graph(self):
        # This method will be called automatically - it now just prepares the UI
        pass
        
    def display_graph(self):
        # This method actually displays the graph when the button is clicked
        student_id = self.master.current_student_id
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT score FROM score WHERE student_id = ?", (student_id,))
            result = cursor.fetchall()
            
        if not result:
            messagebox.showinfo("No Data", "You haven't completed any quizzes yet.")
            return
            
        student_scores = ([row[0] for row in result])
        quizzes_count = len(student_scores)
        
        # Create integer x-axis values from 1 to the number of quizzes
        x = list(range(1, quizzes_count + 1))
        
        # Create a new figure
        plt.figure(figsize=(8, 6))
        
        plt.plot(x, student_scores, marker='o', linestyle='-', color='b', label=f"Student {student_id} progress")
        plt.xlabel("Quizzes Completed")
        plt.ylabel("Percentage")
        
        # Set x-ticks to be integers only
        plt.xticks(x)
        
        plt.ylim(0, 100)
        plt.title(f"Progress for Student {student_id}")
        plt.legend()
        
        # Display the graph in a non-blocking way
        plt.show(block=False)
        
        
    



class MyQuizzes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nesw")

        # Initialize variables
        self.questions = []  # List to hold the question data
        self.start_quiz_buttons = []
        self.current_question_index = 0
        self.answers = []
        self.finished = False  # Keep track if quiz is finished

        # Create a frame for question content (question and answer input)
        self.question_frame = tk.Frame(self)
        self.question_frame.pack(pady=10)

        # Back button to navigate back to menu
        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.menu_frame))
        back_button.pack(pady=10)

        # Question navigation buttons (initially hidden)
        self.next_button = tk.Button(self, text="Next", command=self.next_question)
        self.back_button = tk.Button(self, text="Back", command=self.prev_question)
        self.finish_button = tk.Button(self, text="Finish Test", command=self.finish_quiz)

        # Initially hide the buttons
        self.next_button.pack_forget()
        self.back_button.pack_forget()
        self.finish_button.pack_forget()  # Hide finish button initially

    def show_quizzes(self):
        counter=0
        student_id = self.master.current_student_id
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()



            # Get the teacher ID associated with the student
            cursor.execute("SELECT teacher_id FROM student WHERE student_id = ?", (student_id,))
            teacher_id = cursor.fetchone()[0]

            # Get all subject names for tests assigned by the teacher
            cursor.execute("SELECT DISTINCT subject_name FROM subject WHERE subject_id IN "
                           "(SELECT subject_id FROM test WHERE teacher_id = ?)", (teacher_id,))
            subject_names = cursor.fetchall()

            for subject in subject_names:
                subject_name = subject[0]

                # Check if the student has already taken a test for this subject
                cursor.execute("""SELECT test.test_id 
                                  FROM test 
                                  JOIN subject ON test.subject_id = subject.subject_id 
                                  WHERE subject.subject_name = ?""", (subject_name,))
                test_id = cursor.fetchone()

                if test_id:
                    test_id = test_id[0]

                    # Check if the student has already completed this test
                    cursor.execute("SELECT COUNT(*) FROM score WHERE test_id = ? AND student_id = ?", 
                                   (test_id, student_id))
                    completed = cursor.fetchone()[0]

                    if completed == 0:  # Only show the test if the student hasn't completed it     
                        start_quiz_button = tk.Button(self, text=subject_name, 
                                                      command=lambda s=subject_name: self.open_test(s))

                        start_quiz_button.pack()
                        self.start_quiz_buttons.append(start_quiz_button)
                        counter=counter+1

        if counter == 0:
            messagebox.showinfo("No Quizzes", "You have no quizzes availible")
            self.master.show_frame(self.master.menu_frame)


    def open_test(self, subject_name):
        # Hide subject selection buttons
        for button in self.start_quiz_buttons:
            button.pack_forget()

        # Fetch test questions from the database
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT subject_id FROM subject WHERE subject_name = ?", (subject_name,))
            subject_id = cursor.fetchone()[0]
            cursor.execute("SELECT test_id FROM test WHERE subject_id = ?", (subject_id,))
            test_id = cursor.fetchall()[0][0]
            self.test_id_get = test_id

            cursor.execute("SELECT question, answer FROM questions WHERE test_id = ?", (test_id,))
            questions_and_answers = cursor.fetchall()

            self.questions = questions_and_answers
            self.answers = [""] * len(self.questions)  # Initialize answer list
            self.current_question_index = 0

        # Show the question and buttons
        self.show_question()
        self.next_button.pack(side="right", padx=10)
        self.back_button.pack(side="left", padx=10)
        self.finish_button.pack(pady=10)  # Now show the finish button when the quiz starts

    def show_question(self):
        # Clear any existing question widgets, but keep the navigation buttons visible
        for widget in self.question_frame.winfo_children():
            widget.pack_forget()

        # Display current question
        question_text = self.questions[self.current_question_index][0]
        self.question_label = tk.Label(self.question_frame, text=question_text)
        self.question_label.pack(pady=10)

        # Answer input field
        self.answer_entry = tk.Entry(self.question_frame)
        self.answer_entry.pack(pady=10)

        # Show current answer if it exists
        if self.answers[self.current_question_index]:
            self.answer_entry.insert(0, self.answers[self.current_question_index])

        # Back button functionality
        if self.current_question_index == 0:
            self.back_button.config(state="disabled")
        else:
            self.back_button.config(state="normal")

        # Next button functionality
        if self.current_question_index == len(self.questions) - 1:
            self.next_button.config(state="disabled")
        else:
            self.next_button.config(state="normal")

    def next_question(self):
        # Save the answer
        self.answers[self.current_question_index] = self.answer_entry.get()

        # Move to the next question
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.show_question()

    def prev_question(self):
        # Save the answer
        self.answers[self.current_question_index] = self.answer_entry.get()

        # Move to the previous question
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()



    def finish_quiz(self):
        student_id = self.master.current_student_id
        test_id = self.test_id_get
        # Save the last answer
        self.answers[self.current_question_index] = self.answer_entry.get()

        # Calculate score
        score = 0
        incorrect_questions = []

        for i in range(len(self.questions)):
            correct_answer = self.questions[i][1]
            user_answer = self.answers[i]

            if user_answer == correct_answer:
                score += 1
            else:
                incorrect_questions.append((self.questions[i][0], correct_answer, user_answer))  # Store (question, correct answer, user answer)

        # Clear the current quiz screen
        for widget in self.winfo_children():
            widget.pack_forget()

        # Display the results
        result_label = tk.Label(self, text=f"Your score is {score}/{len(self.questions)}", font=("Arial", 14, "bold"))
        result_label.pack(pady=10)

        # If user got any wrong answers, display them
        if incorrect_questions:
            incorrect_label = tk.Label(self, text="Questions you got wrong:", font=("Arial", 12, "bold"))
            incorrect_label.pack(pady=5)

            for question, correct, user in incorrect_questions:
                question_label = tk.Label(self, text=f"Q: {question}\nYour answer: {user}\nCorrect answer: {correct}", fg="red", justify="left")
                question_label.pack(pady=5)

        # Button to return to the main menu
        menu_button = tk.Button(self, text="Back to Menu", command=lambda: self.master.show_frame(self.master.student_frame))
        menu_button.pack(pady=10)

        score=(score/len(self.questions)*100)

        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO score (test_id, student_id, score) VALUES (?, ?, ?);", 
                   (test_id, student_id, score))
            db.commit()

    def reset(self):
        """Resets the MyQuizzes frame to its default state, ensuring a fresh start."""
        # Clear all widgets in the frame (removes any lingering result screens)
        for widget in self.winfo_children():
            widget.pack_forget()

        # Reinitialize question-related variables
        self.questions = []
        self.answers = []
        self.current_question_index = 0
        self.finished = False

        # Reset the button list
        self.start_quiz_buttons.clear()

        # Recreate the question frame
        self.question_frame = tk.Frame(self)
        self.question_frame.pack(pady=10)

        # Re-add the back button
        back_button = tk.Button(self, text="Back", command=lambda: self.master.show_frame(self.master.menu_frame))
        back_button.pack(pady=10)

        # Hide navigation buttons initially
        self.next_button.pack_forget()
        self.back_button.pack_forget()
        self.finish_button.pack_forget()

        # Reload available quizzes
        self.show_quizzes()

        # Show quizzes again
        # You can also submit the answers to the database or perform any other task here
        # For example, save answers to a database, or display a summary, etc.




















class TeacherFirstMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nesw")

        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.menu_frame))
        back_button.pack(pady=10)

        create_quiz_button = tk.Button(self, text="Create Quiz",
                                       command=lambda: parent.show_frame(parent.create_quiz_frame))
        create_quiz_button.pack()

        def reset_and_show_students():
            # Reset the MyStudentsMenu frame
            parent.my_students_frame = MyStudentsMenu(parent)
            parent.show_frame(parent.my_students_frame)

        my_students_button = tk.Button(self, text="My Students", command=reset_and_show_students)
        my_students_button.pack()



class MyStudentsMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nesw")

        self.selected_student = tk.StringVar()
        self.selected_student.trace("w", self.option_choice)

        self.selected_teacher = tk.StringVar()
        self.selected_teacher.trace("w", self.teacher_choice)

        self.view_progress_button = None
        self.set_new_password_button = None
        self.change_teacher_button = None
        self.delete_student_button = None

        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.menu_frame))
        back_button.pack(pady=10)

    def show_students(self):
        teacher_id = self.master.current_teacher_id
        print(teacher_id)
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            # order b
            cursor.execute(
                "SELECT student_first_name, student_surname FROM student WHERE teacher_id = ? ORDER BY student_first_name, student_surname",
                (teacher_id,))

            students = cursor.fetchall()
            if students:
                # Convert tuples to formatted strings
                students = [f"{first} {surname}" for first, surname in students]
                self.selected_student.set(students[0])
            else:
                messagebox.showwarning("No Students", "No students found for this teacher.")
                return

        self.selected_student.set(students[0])

        self.dropdown = tk.OptionMenu(self, self.selected_student, *students)
        self.dropdown.pack()

        self.view_progress_button = tk.Button(self, text="View Progress", command=lambda: self.view_progress())
        self.view_progress_button.pack()

        self.set_new_password_button = tk.Button(self, text="Set new password", command=self.pass_selected_student)
        self.set_new_password_button.pack()

        self.change_teacher_button = tk.Button(self, text="Change teacher", command=lambda: self.change_teacher())
        self.change_teacher_button.pack()

        self.delete_student_button = tk.Button(self, text="Delete student", command=lambda: self.delete_student())
        self.delete_student_button.pack()

    def option_choice(self, *args):
        self.current_student = self.selected_student.get()

    def teacher_choice(self, *args):
        self.current_teacher = self.selected_teacher.get()

    def pass_selected_student(self):
        student_str = self.selected_student.get()  # Get the formatted string, e.g., "John Doe"

        # Split the string into first name and surname
        first_name, surname = student_str.split()

        # Now you can use first_name and surname directly
        self.set_new_password(first_name, surname)

    def set_new_password(self, first_name, surname):
        self.dropdown.pack_forget()
        self.view_progress_button.pack_forget()
        self.set_new_password_button.pack_forget()
        self.change_teacher_button.pack_forget()
        self.delete_student_button.pack_forget()

        tk.Label(self, text="Set New Password", font=("Helvetica", 16)).pack(pady=10)

        tk.Label(self, text="New Password:").pack()
        self.new_password_entry = tk.Entry(self)
        self.new_password_entry.pack()

        set_password_button = tk.Button(self, text="Set Password",
                                        command=lambda: self.set_password(first_name, surname))
        set_password_button.pack(pady=10)

    def set_password(self, first_name, surname):
        password = self.new_password_entry.get()
        if password.strip == "":
            messagebox.showerror("Error, Please fill in all fields")
        else:
            with sqlite3.connect("micro.db") as db:
                cursor = db.cursor()
                cursor.execute("UPDATE student SET password = ? WHERE student_first_name = ? AND student_surname = ? ",
                               (password, first_name, surname))
                db.commit()
            messagebox.showinfo("Success", "Password set successfully")
            self.master.show_frame(self.master.teacher_frame)

    def delete_student(self):
        self.dropdown.pack_forget()
        self.view_progress_button.pack_forget()
        self.set_new_password_button.pack_forget()
        self.change_teacher_button.pack_forget()
        self.delete_student_button.pack_forget()

        # ask the user if they are sure they want to delete the student
        result = messagebox.askyesno("Delete Student", "Are you sure you want to delete this student?")

        student_str = self.selected_student.get()
        first_name, surname = student_str.split()
        if result == True:
            with sqlite3.connect("micro.db") as db:
                # get the student id number
                cursor = db.cursor()
                cursor.execute("SELECT student_id FROM student WHERE student_first_name = ? AND student_surname = ?",
                               (first_name, surname))
                student_id = cursor.fetchone()[0]
                # delete the student
                # delete students score
                cursor.execute("DELETE FROM score WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM student WHERE student_id = ?", (student_id,))
                db.commit()
            messagebox.showinfo("Success", "Student deleted successfully")
        else:
            messagebox.showinfo("Cancelled", "Student not deleted")
            self.master.show_frame(self.master.teacher_frame)

    def change_teacher(self):
        self.dropdown.pack_forget()
        self.view_progress_button.pack_forget()
        self.set_new_password_button.pack_forget()
        self.change_teacher_button.pack_forget()
        self.delete_student_button.pack_forget()

        student_str = self.selected_student.get()
        first_name, surname = student_str.split()
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT teacher_first_name, teacher_surname FROM teacher ORDER BY teacher_first_name, teacher_surname")
            teachers = cursor.fetchall()
            if teachers:
                teachers = [f"{first} {surname}" for first, surname in teachers]
                self.selected_teacher.set(teachers[0])

                self.dropdown = tk.OptionMenu(self, self.selected_teacher, *teachers)

                self.dropdown.pack()
                # create confirm button
                confirm_button = tk.Button(self, text="Confirm", command=lambda: self.teacher_confirm())
                confirm_button.pack(pady=10)

    def teacher_confirm(self):
        student_str = self.selected_student.get()
        first_name, surname = student_str.split()
        teachers = self.selected_teacher.get()
        teacher_first_name, teacher_surname = teachers.split()

        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT teacher_id FROM teacher WHERE teacher_first_name = ? AND teacher_surname = ?",
                           (teacher_first_name, teacher_surname))
            teacher_id = cursor.fetchone()[0]
            cursor.execute("UPDATE student SET teacher_id = ? WHERE student_first_name = ? AND student_surname = ?",
                           (teacher_id, first_name, surname))
            db.commit()
        messagebox.showinfo("Success", "Teacher succefully changed")
        self.master.show_frame(self.master.teacher_frame)

    def view_progress(self):
        student_str = self.selected_student.get()
        first_name, surname = student_str.split()

        with sqlite3.connect("micro.db") as db:
            # get the student id number
            cursor = db.cursor()
            cursor.execute("SELECT student_id FROM student WHERE student_first_name = ? AND student_surname = ?",
                           (first_name, surname))
            student_id = cursor.fetchone()[0]

        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT score FROM score WHERE student_id = ?", (student_id,))
            result = cursor.fetchall()
            
        if not result:
            messagebox.showinfo("No Data", f"Student {student_id} hasn't completed any quizzes yet.")
            return
            
        student_scores = ([row[0] for row in result])
        quizzes_count = len(student_scores)
        
        # Create integer x-axis values
        x = list(range(1, quizzes_count + 1))
        
        # Create a new figure with a title
        plt.figure(figsize=(8, 6))
        
        plt.plot(x, student_scores, marker='o', linestyle='-', color='b', label=f"Student {student_id} progress")
        plt.xlabel("Quizzes Completed")
        plt.ylabel("Percentage")
        
        # Set x-ticks to be integers only
        plt.xticks(x)
        
        plt.ylim(0, 100)
        plt.title(f"Progress for Student {student_id}")
        plt.legend()
        
        # Show the plot in a non-blocking way so the user can return to the app
        plt.show(block=False)
        
        # Create a "back to menu" button 
        back_menu_button = tk.Button(self, text="Back to Menu", command=lambda: self.master.show_frame(self.master.teacher_frame))
        back_menu_button.pack(pady=10)
        


class CreateQuizMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nesw")

        self.quiz_question = []
        self.quiz_answer = []
        self.max_questions = 10

        back_button = tk.Button(self, text="Back", command=lambda: parent.show_frame(parent.teacher_frame))
        back_button.pack(pady=10)

        self.subject_label = tk.Label(self, text="Enter quiz subject")
        self.subject_label.pack()
        self.subject_entry = tk.Entry(self)
        self.subject_entry.pack()

        self.confirm_subject_button = tk.Button(self, text="Confirm", command=self.confirm_subject)
        self.confirm_subject_button.pack()

        self.question_counter_label = tk.Label(self, text="Question: 0/10")

        self.question_label = tk.Label(self, text="Question")
        self.question_entry = tk.Entry(self)

        self.answer_label = tk.Label(self, text="Answer")
        self.answer_entry = tk.Entry(self)

        self.submit_button = tk.Button(self, text="Submit", command=self.submit)

    def confirm_subject(self):
        self.subject_label.pack_forget()
        self.subject_entry.pack_forget()
        self.confirm_subject_button.pack_forget()

        self.question_counter_label.pack()
        self.question_label.pack()
        self.question_entry.pack()
        self.answer_label.pack()
        self.answer_entry.pack()
        self.submit_button.pack()

    def submit(self):
        question = self.question_entry.get().strip()
        answer = self.answer_entry.get().strip()

        if question == "":
            messagebox.showinfo("Error", "Please enter a question")
        elif answer == "":
            messagebox.showinfo("Error", "Please enter an answer")
        else:
            self.quiz_question.append(question)
            self.quiz_answer.append(answer)
            self.question_entry.delete(0, tk.END)
            self.answer_entry.delete(0, tk.END)

            current_count = len(self.quiz_question)
            self.question_counter_label.config(text=f"Question: {current_count}/10")

            if current_count == 1:
                self.create_test_button = tk.Button(self, text="Create Test", command=self.create_test)
                self.create_test_button.pack()

            if current_count >= self.max_questions:
                self.submit_button.config(state=tk.DISABLED)

    def create_test(self):
        subject_name = self.subject_entry.get().strip()
        subject_id = generate_subject_id()
        teacher_id = self.master.current_teacher_id
        create_new_subject(subject_name, subject_id)
        test_id = generate_new_id("TEST")

        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()

            # Insert test metadata (only once per test)
            cursor.execute("INSERT INTO test (test_id, subject_id, teacher_id) VALUES (?, ?, ?);", 
                           (test_id, subject_id, teacher_id))

            # Insert each question into the questions table
            for i in range(len(self.quiz_question)):
                cursor.execute("INSERT INTO questions (test_id, question, answer) VALUES (?, ?, ?);", 
                               (test_id, self.quiz_question[i], self.quiz_answer[i]))

            db.commit()

        messagebox.showinfo("Success", "Quiz created successfully!")
        self.master.show_frame(self.master.teacher_frame)


    def reset(self):
        self.quiz_question = []
        self.quiz_answer = []
        self.subject_entry.delete(0, tk.END)
        self.question_entry.delete(0, tk.END)
        self.answer_entry.delete(0, tk.END)
        self.submit_button.config(state=tk.NORMAL)
        self.question_counter_label.config(text="Question: 0/10")

        # Show initial state
        self.subject_label.pack()
        self.subject_entry.pack()
        self.confirm_subject_button.pack()

        # Hide other elements
        self.question_counter_label.pack_forget()
        self.question_label.pack_forget()
        self.question_entry.pack_forget()
        self.answer_label.pack_forget()
        self.answer_entry.pack_forget()
        self.submit_button.pack_forget()


def generate_new_id(choice):
    if choice == "STUDENT":
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(student_id) FROM student")
            count = cursor.fetchone()[0] or 0
            count = count + 1
            max_digits = 4
            count_str = str(count).zfill(max_digits)
            new_id = 'S' + count_str
            return new_id
    elif choice == "TEACHER":
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(teacher_id) FROM teacher")
            count = cursor.fetchone()[0] or 0
            count = count + 1
            max_digits = 4
            count_str = str(count).zfill(max_digits)
            new_id = 'T' + count_str
            return new_id
    elif choice == "TEST":
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(test_id) FROM test")
            count = cursor.fetchone()[0] or 0
            count = count + 1
            max_digits = 4
            count_str = str(count).zfill(max_digits)
            new_id = 'Q' + count_str
            return new_id
    elif choice == "SUBJECT":
        with sqlite3.connect("micro.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(subject_id) FROM subject")
            count = cursor.fetchone()[0] or 0
            count = count + 1
            max_digits = 4
            count_str = str(count).zfill(max_digits)
            new_id = 'SID' + count_str
            return new_id


def generate_subject_id():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT subject_id FROM subject ORDER BY subject_id DESC LIMIT 1")
        last_id = cursor.fetchone()

        if last_id:
            last_number = int(last_id[0][3:])  # Extract numeric part after 'SID'
            new_number = last_number + 1
        else:
            new_number = 1  # If table is empty, start with 1

        new_id = f"SID{str(new_number).zfill(4)}"  # Format with leading zeros
        return new_id




def create_teacher():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS teacher (
            teacher_id TEXT NOT NULL PRIMARY KEY CHECK(LENGTH(teacher_id) = 5),
            teacher_first_name TEXT NOT NULL,
            teacher_surname TEXT NOT NULL,
            password TEXT NOT NULL
        );"""
        cursor.execute(sql)


def create_student():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS student (
            student_id TEXT NOT NULL PRIMARY KEY CHECK(LENGTH(student_id) = 5),
            teacher_id TEXT NOT NULL,
            student_first_name TEXT NOT NULL,
            student_surname TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
        );"""
        cursor.execute(sql)


def create_subject():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS subject (
            subject_id TEXT NOT NULL PRIMARY KEY,
            subject_name TEXT NOT NULL
        );"""
        cursor.execute(sql)


def create_test():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS test (
            test_id TEXT NOT NULL PRIMARY KEY CHECK(LENGTH(test_id) = 5),
            subject_id TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id),
            FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
        );"""
        cursor.execute(sql)


def create_score():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS score (
            test_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            PRIMARY KEY (test_id, student_id),
            FOREIGN KEY (test_id) REFERENCES test(test_id),
            FOREIGN KEY (student_id) REFERENCES student(student_id)
        );"""
        cursor.execute(sql)

def create_questions():
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        sql ="""CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY (test_id) REFERENCES test(test_id)
        );"""
        cursor.execute(sql)



create_teacher()
create_student()
create_test()
create_score()
create_subject()
create_questions()


def create_new_stduent(studentnum, first_name, surname, password):
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        sql = """ INSERT INTO student (student_id, teacher_id, student_first_name, student_surname, password)
        VALUES(studentnum,first_name,surname,password);
            """

        cursor.execute(sql)


def check_username(username):
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT student_id FROM student WHERE student_id = ?
            UNION 
            SELECT teacher_id FROM teacher WHERE teacher_id = ?""", (username, username))
        result = cursor.fetchone()  # Fetch the first match

        return result is not None


def check_password(user_id, user_input):
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT password FROM student WHERE student_id = ?
            UNION 
            SELECT password FROM teacher WHERE teacher_id = ?""", (user_id, user_id))
        result = cursor.fetchone()  # Fetch password

        if result[0] == user_input:
            return True  # Password matches
        return False


def create_new_subject(subject_name, subject_id):
    with sqlite3.connect("micro.db") as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO subject (subject_id, subject_name) VALUES (?, ?)", (subject_id, subject_name))
        db.commit()


if __name__ == "__main__":
    app = App()
    app.mainloop()

