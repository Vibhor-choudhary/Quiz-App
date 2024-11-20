import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
import random
import html

from database import DatabaseManager
from questions import QuestionManager


class QuizApp:
    def __init__(self):
        self.root = ttk.Window(themename="superhero")
        self.root.title("Quiz Master")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        self.db_manager = DatabaseManager()
        self.question_manager = QuestionManager()

        self.current_user = None
        self.current_user_id = None
        self.current_questions = []
        self.current_question_index = 0
        self.score = 0
        self.current_category = None  # Track the current quiz category

        self.create_login_frame()

    def create_login_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = ttk.Frame(self.root, padding=50)
        login_frame.grid(row=0, column=0, sticky="nsew")

        title_label = ttk.Label(
            login_frame,
            text="Quiz Master",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 30))

        username_frame = ttk.Frame(login_frame)
        username_frame.pack(fill=X, pady=10)

        ttk.Label(username_frame, text="Username:", font=("Helvetica", 12)).pack(side=LEFT)
        self.username_entry = ttk.Entry(username_frame, font=("Helvetica", 12))
        self.username_entry.pack(side=RIGHT, expand=YES, fill=X)

        password_frame = ttk.Frame(login_frame)
        password_frame.pack(fill=X, pady=10)

        ttk.Label(password_frame, text="Password:", font=("Helvetica", 12)).pack(side=LEFT)
        self.password_entry = ttk.Entry(password_frame, show="*", font=("Helvetica", 12))
        self.password_entry.pack(side=RIGHT, expand=YES, fill=X)

        button_frame = ttk.Frame(login_frame)
        button_frame.pack(fill=X, pady=20)

        login_button = ttk.Button(
            button_frame,
            text="Login",
            command=self.login,
            bootstyle="success-outline"
        )
        login_button.pack(side=LEFT, expand=YES, padx=5)

        register_button = ttk.Button(
            button_frame,
            text="Register",
            command=self.register,
            bootstyle="info-outline"
        )
        register_button.pack(side=RIGHT, expand=YES, padx=5)

        leaderboard_button = ttk.Button(
            login_frame,
            text="View Leaderboard",
            command=self.show_leaderboard,
            bootstyle="secondary-outline"
        )
        leaderboard_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user_data = self.db_manager.validate_login(username, password)
        if user_data:
            self.current_user = username
            self.current_user_id = user_data[0]
            self.create_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid Credentials")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.db_manager.register_user(username, password):
            messagebox.showinfo("Success", "Registration Successful")
        else:
            messagebox.showerror("Error", "Username already exists")

    def create_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        dashboard_frame = ttk.Frame(self.root, padding=50)
        dashboard_frame.grid(row=0, column=0, sticky="nsew")

        welcome_label = ttk.Label(
            dashboard_frame,
            text=f"Welcome, {self.current_user}!",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        )
        welcome_label.pack(pady=(0, 30))

        categories = ["General Knowledge", "Science", "Computer", "Mathematics"]
        for category in categories:
            btn = ttk.Button(
                dashboard_frame,
                text=category,
                command=lambda cat=category: self.start_quiz(cat),
                bootstyle="secondary-outline",
                width=30
            )
            btn.pack(pady=10)

        score_button = ttk.Button(
            dashboard_frame,
            text="View Scores",
            command=self.show_scores,
            bootstyle="secondary-outline",
            width=30
        )
        score_button.pack(pady=10)

        exit_button = ttk.Button(
            dashboard_frame,
            text="Log Out",
            command=self.create_login_frame,
            bootstyle="danger-outline",
            width=30
        )
        exit_button.pack(pady=10)

    def start_quiz(self, category):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.current_category = category  # Store the category
        self.current_questions = self.question_manager.fetch_questions(category)
        self.current_question_index = 0
        self.score = 0
        self.create_quiz_frame()

    def create_quiz_frame(self):
        quiz_frame = ttk.Frame(self.root, padding=30)
        quiz_frame.grid(row=0, column=0, sticky="nsew")

        info_frame = ttk.Frame(quiz_frame)
        info_frame.pack(fill=X, pady=(0, 20))

        self.question_counter_label = ttk.Label(
            info_frame,
            text=f"Question {self.current_question_index + 1}/{len(self.current_questions)}",
            font=("Helvetica", 12)
        )
        self.question_counter_label.pack(side=RIGHT)

        self.question_label = ttk.Label(
            quiz_frame,
            text="",
            font=("Helvetica", 14),
            wraplength=500,
            anchor="center"
        )
        self.question_label.pack(pady=20)

        self.answer_buttons = []
        for i in range(4):
            button = ttk.Button(
                quiz_frame,
                text="",
                command=lambda i=i: self.check_answer(i),
                width=50,
                bootstyle="outline-secondary"
            )
            button.pack(pady=10)
            self.answer_buttons.append(button)

        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]
            decoded_question = html.unescape(question['question'])
            self.question_label.config(text=decoded_question)
            self.question_counter_label.config(
                text=f"Question {self.current_question_index + 1}/{len(self.current_questions)}")

            answers = question['incorrect_answers'] + [question['correct_answer']]
            answers = [html.unescape(ans) for ans in answers]
            random.shuffle(answers)

            for i, button in enumerate(self.answer_buttons):
                button.config(text=answers[i])
        else:
            self.display_score()

    def check_answer(self, answer_index):
        question = self.current_questions[self.current_question_index]
        if self.answer_buttons[answer_index]['text'] == html.unescape(question['correct_answer']):
            self.score += 1
            messagebox.showinfo("Correct!", "Your answer is correct.")
        else:
            messagebox.showinfo("Incorrect!",
                                f"Sorry, the correct answer was {html.unescape(question['correct_answer'])}.")

        self.next_question()

    def next_question(self):
        self.current_question_index += 1
        self.display_question()

    def display_score(self):
        plt.close('all')
        score_message = f"Quiz complete!\nYour score is {self.score}/{len(self.current_questions)}"
        messagebox.showinfo("Quiz Complete", score_message)

        # Use the stored category
        self.db_manager.record_score(
            self.current_user_id,
            self.current_category,  # Use stored category instead of trying to get it from questions
            self.score,
            len(self.current_questions)
        )

        self.plot_score_graph()
        self.create_dashboard()  # Go back to dashboard after quiz

    def plot_score_graph(self):
        plt.figure(figsize=(6, 4))

        labels = ['Correct', 'Incorrect']
        sizes = [self.score, len(self.current_questions) - self.score]
        colors = ['#66b3ff', '#ff9999']

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Quiz Score')
        plt.tight_layout()
        plt.show()

    def show_scores(self):
        scores = self.db_manager.get_user_scores(self.current_user_id)

        if not scores:
            messagebox.showinfo("Scores", "No quiz history available.")
            return

        scores_window = ttk.Toplevel(self.root)
        scores_window.title("Your Quiz History")
        scores_window.geometry("500x600")

        # Create a frame for the scores
        scores_frame = ttk.Frame(scores_window, padding=20)
        scores_frame.pack(fill=BOTH, expand=YES)

        # Add a title
        ttk.Label(
            scores_frame,
            text=f"Quiz History for {self.current_user}",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(0, 20))

        # Create text widget to display scores
        text_widget = tk.Text(scores_frame, wrap=tk.WORD, width=50, height=20)
        text_widget.pack(pady=10)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(scores_frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Insert scores into text widget
        for idx, (username, category, score, correct, incorrect, date) in enumerate(scores, start=1):
            success_rate = (correct / (correct + incorrect)) * 100 if (correct + incorrect) > 0 else 0
            score_text = (
                f"\n{idx}. Quiz Date: {date}\n"
                f"   Category: {category}\n"
                f"   Total Score: {score}\n"
                f"   Correct Answers: {correct}\n"
                f"   Incorrect Answers: {incorrect}\n"
                f"   Success Rate: {success_rate:.1f}%\n"
                f"{'─' * 40}\n"
            )
            text_widget.insert(tk.END, score_text)

        # Make text widget read-only
        text_widget.configure(state='disabled')

        # Add a close button
        ttk.Button(
            scores_frame,
            text="Close",
            command=scores_window.destroy,
            style="secondary.TButton"
        ).pack(pady=10)

    def show_leaderboard(self):
        leaderboard = self.db_manager.get_leaderboard()
        leaderboard_str = "Leaderboard:\n\n"
        for idx, (username, total_score, total_quizzes) in enumerate(leaderboard, start=1):
            leaderboard_str += f"{idx}. {username} - {total_score} points in {total_quizzes} quizzes\n"

        messagebox.showinfo("Leaderboard", leaderboard_str)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = QuizApp()
    app.run()
