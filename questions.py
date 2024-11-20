import requests
import random

class QuestionManager:
    def __init__(self):
        self.base_url = "https://opentdb.com/api.php"

    def fetch_questions(self, category, difficulty='medium', limit=10):
        categories = {
            "General Knowledge": 9,
            "Science": 17,
            "Computer": 18,
            "Mathematics": 19
        }

        params = {
            'amount': limit,
            'category': categories.get(category, 9),
            'difficulty': difficulty,
            'type': 'multiple'
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        processed_questions = []
        for question in data['results']:
            processed_question = {
                'question': question['question'],
                'correct_answer': question['correct_answer'],
                'incorrect_answers': question['incorrect_answers']
            }
            processed_questions.append(processed_question)

        return processed_questions