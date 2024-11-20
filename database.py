import sqlite3


class DatabaseManager:
    def __init__(self, db_name='quiz_database.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # User Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                total_score INTEGER DEFAULT 0,
                total_quizzes INTEGER DEFAULT 0
            )
        ''')

        # Drop existing quiz_history table if it exists
        self.cursor.execute('DROP TABLE IF EXISTS quiz_history')

        # Create new quiz_history table with all required columns
        self.cursor.execute('''
            CREATE TABLE quiz_history (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                category TEXT,
                score INTEGER,
                correct_answers INTEGER,
                incorrect_answers INTEGER,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        self.connection.commit()

    def register_user(self, username, password):
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validate_login(self, username, password):
        self.cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )
        return self.cursor.fetchone()

    def record_score(self, user_id, category, score, total_questions):
        correct_answers = score
        incorrect_answers = total_questions - score

        self.cursor.execute(
            """INSERT INTO quiz_history 
            (user_id, category, score, correct_answers, incorrect_answers) 
            VALUES (?, ?, ?, ?, ?)""",
            (user_id, category, score, correct_answers, incorrect_answers)
        )
        self.connection.commit()

        self.cursor.execute(
            "UPDATE users SET total_score = total_score + ?, total_quizzes = total_quizzes + 1 WHERE id = ?",
            (score, user_id)
        )
        self.connection.commit()

    def get_user_scores(self, user_id):
        self.cursor.execute('''
            SELECT 
                u.username,
                q.category,
                q.score,
                q.correct_answers,
                q.incorrect_answers,
                q.date
            FROM quiz_history q
            JOIN users u ON q.user_id = u.id
            WHERE q.user_id = ?
            ORDER BY q.date DESC
        ''', (user_id,))
        return self.cursor.fetchall()

    def get_leaderboard(self):
        self.cursor.execute('''
            SELECT username, total_score, total_quizzes 
            FROM users 
            ORDER BY total_score DESC 
            LIMIT 10
        ''')
        return self.cursor.fetchall()