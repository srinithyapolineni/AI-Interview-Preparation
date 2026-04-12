"""
question_generator.py
Generates interview questions using:
  1. Curated local question bank (fast, no API cost)
  2. OpenAI API for dynamic / role-specific questions
"""

import os
import random
from typing import Optional
from openai import OpenAI

# ── Curated Question Bank ──────────────────────────────────────────────────

QUESTION_BANK = {
    "Data Structures": {
        "Easy":   [
            "What is an array and how does it differ from a linked list?",
            "Explain what a stack is and give a real-world example.",
            "What is a queue? How is it different from a stack?",
        ],
        "Medium": [
            "Explain the difference between BFS and DFS with examples.",
            "What is a binary search tree? What are its properties?",
            "How does a hash table work? What is a hash collision?",
        ],
        "Hard":   [
            "Explain AVL trees and how rotations maintain balance.",
            "What is a segment tree and when would you use it?",
            "Describe the time and space complexity of Dijkstra's algorithm.",
        ],
    },
    "Algorithms": {
        "Easy":   [
            "What is the difference between linear and binary search?",
            "Explain bubble sort and its time complexity.",
            "What does O(n log n) mean?",
        ],
        "Medium": [
            "Explain merge sort with an example.",
            "What is dynamic programming? Give an example problem.",
            "What is the sliding window technique?",
        ],
        "Hard":   [
            "Explain the difference between greedy algorithms and dynamic programming.",
            "How would you solve the Travelling Salesman Problem approximately?",
            "What is amortized time complexity? Give an example.",
        ],
    },
    "Python": {
        "Easy":   [
            "What is the difference between a list and a tuple in Python?",
            "Explain Python's GIL (Global Interpreter Lock).",
            "What are Python decorators?",
        ],
        "Medium": [
            "How does Python's garbage collection work?",
            "What is the difference between @staticmethod and @classmethod?",
            "Explain Python generators and the yield keyword.",
        ],
        "Hard":   [
            "How would you implement a thread-safe singleton in Python?",
            "Explain metaclasses in Python with a use case.",
            "What are the differences between multiprocessing and multithreading in Python?",
        ],
    },
    "SQL": {
        "Easy":   [
            "What is the difference between WHERE and HAVING in SQL?",
            "Explain the different types of JOINs in SQL.",
            "What is a primary key vs a foreign key?",
        ],
        "Medium": [
            "What are window functions in SQL? Give an example.",
            "Explain database normalization — 1NF, 2NF, 3NF.",
            "What is an index and how does it improve query performance?",
        ],
        "Hard":   [
            "How would you optimise a slow SQL query? Walk me through your process.",
            "Explain ACID properties in database transactions.",
            "What is the difference between clustered and non-clustered indexes?",
        ],
    },
    "Machine Learning": {
        "Easy":   [
            "What is the difference between supervised and unsupervised learning?",
            "Explain overfitting and how to prevent it.",
            "What is a confusion matrix?",
        ],
        "Medium": [
            "Explain the bias-variance tradeoff.",
            "What is regularization? Explain L1 vs L2.",
            "How does gradient descent work?",
        ],
        "Hard":   [
            "Explain the backpropagation algorithm in neural networks.",
            "What is the vanishing gradient problem and how is it solved?",
            "Compare Random Forest and Gradient Boosting — when would you choose each?",
        ],
    },
    "Behavioral": {
        "Easy":   [
            "Tell me about yourself and your background.",
            "Why are you interested in this role?",
            "What are your greatest strengths?",
        ],
        "Medium": [
            "Describe a time you faced a difficult technical problem. How did you solve it?",
            "Tell me about a project you are most proud of.",
            "How do you handle tight deadlines?",
        ],
        "Hard":   [
            "Describe a situation where you disagreed with a teammate. How did you handle it?",
            "Tell me about a time you failed. What did you learn?",
            "How do you prioritise when you have multiple urgent tasks?",
        ],
    },
    "System Design": {
        "Easy":   [
            "What is the difference between SQL and NoSQL databases?",
            "Explain what a REST API is.",
            "What is caching and why is it important?",
        ],
        "Medium": [
            "How would you design a URL shortening service like bit.ly?",
            "Explain horizontal vs vertical scaling.",
            "What is a load balancer and why is it used?",
        ],
        "Hard":   [
            "Design a distributed messaging system like WhatsApp.",
            "How would you design Twitter's feed algorithm?",
            "Explain CAP theorem and its implications for distributed systems.",
        ],
    },
}

DEFAULT_TOPICS_PER_ROLE = {
    "Software Developer":  ["Data Structures", "Algorithms", "Python", "System Design", "Behavioral"],
    "Data Analyst":        ["SQL", "Python", "Behavioral"],
    "AI / ML Engineer":    ["Machine Learning", "Python", "Behavioral"],
    "Backend Developer":   ["System Design", "SQL", "Python", "Behavioral"],
    "Frontend Developer":  ["Python", "Behavioral"],
    "Full Stack Developer": ["System Design", "SQL", "Python", "Behavioral"],
    "Data Scientist":      ["Machine Learning", "SQL", "Python", "Behavioral"],
}


class QuestionGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    # ── Public API ─────────────────────────────────────────────────────────

    def generate(self, role: str, difficulty: str, topic: Optional[str] = None) -> dict:
        """
        Returns:
            {
                "question": str,
                "topic": str,
                "difficulty": str,
                "source": "bank" | "ai",
                "hint": str          # optional hint for the user
            }
        """
        chosen_topic = topic or self._pick_topic(role)

        # Try AI generation first (richer, role-specific)
        if self.client:
            try:
                return self._generate_with_ai(role, difficulty, chosen_topic)
            except Exception:
                pass  # Fall back to question bank

        return self._generate_from_bank(difficulty, chosen_topic)

    # ── Internal helpers ───────────────────────────────────────────────────

    def _pick_topic(self, role: str) -> str:
        topics = DEFAULT_TOPICS_PER_ROLE.get(role, ["Behavioral"])
        return random.choice(topics)

    def _generate_from_bank(self, difficulty: str, topic: str) -> dict:
        topic_questions = QUESTION_BANK.get(topic, QUESTION_BANK["Behavioral"])
        diff_questions  = topic_questions.get(difficulty, topic_questions["Medium"])
        question        = random.choice(diff_questions)
        return {
            "question":   question,
            "topic":      topic,
            "difficulty": difficulty,
            "source":     "bank",
            "hint":       self._get_hint(topic),
        }

    def _generate_with_ai(self, role: str, difficulty: str, topic: str) -> dict:
        prompt = (
            f"Generate one {difficulty}-level interview question for a {role} candidate "
            f"on the topic: {topic}. "
            "Return ONLY the question text, nothing else."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.8,
        )
        question = response.choices[0].message.content.strip()
        return {
            "question":   question,
            "topic":      topic,
            "difficulty": difficulty,
            "source":     "ai",
            "hint":       self._get_hint(topic),
        }

    @staticmethod
    def _get_hint(topic: str) -> str:
        hints = {
            "Data Structures": "Think about time and space complexity in your answer.",
            "Algorithms":      "Mention Big-O notation and walk through your logic step by step.",
            "Python":          "Use a code example if possible to demonstrate your point.",
            "SQL":             "Consider mentioning performance implications where relevant.",
            "Machine Learning":"Include practical examples or real-world applications.",
            "Behavioral":      "Use the STAR method: Situation, Task, Action, Result.",
            "System Design":   "Start with requirements, then scale, then edge cases.",
        }
        return hints.get(topic, "Be clear, concise, and use examples where possible.")

    def generate_from_resume(self, resume_text: str, role: str,
                              difficulty: str, num_questions: int) -> list:
        """Generate personalized questions based on resume content."""
        if self.client:
            try:
                return self._resume_questions_ai(resume_text, role, difficulty, num_questions)
            except Exception:
                pass
        return self._resume_questions_fallback(resume_text, role, difficulty, num_questions)

    def _resume_questions_ai(self, resume_text: str, role: str,
                              difficulty: str, num_questions: int) -> list:
        prompt = f"""
You are an expert technical interviewer. Analyse this resume and generate {num_questions}
targeted {difficulty}-level interview questions for a {role} position.

Resume:
{resume_text[:3000]}

Return ONLY a JSON array like this (no extra text):
[
  {{"question": "...", "reason": "Based on your experience with..."}},
  ...
]
"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        import json
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    def _resume_questions_fallback(self, resume_text: str, role: str,
                                    difficulty: str, num_questions: int) -> list:
        """NLP-based resume question generation without OpenAI."""
        text_lower = resume_text.lower()
        questions  = []

        skill_map = {
            "python":      ("Tell me about your Python experience and a challenging project you built.", "Python skills mentioned"),
            "java":        ("Describe a complex Java application you developed.", "Java skills mentioned"),
            "sql":         ("Walk me through a complex SQL query you wrote and why you designed it that way.", "SQL skills mentioned"),
            "machine learning": ("Explain a machine learning model you built — what problem it solved.", "ML experience mentioned"),
            "react":       ("Describe a React project you built — what state management did you use?", "React skills mentioned"),
            "django":      ("How did you use Django in your projects? What challenges did you face?", "Django mentioned"),
            "git":         ("Describe your Git workflow in a team project.", "Git mentioned"),
            "aws":         ("What AWS services have you used and for what purposes?", "AWS mentioned"),
            "docker":      ("Explain how you used Docker and what problems it solved.", "Docker mentioned"),
            "api":         ("Describe an API you designed or built. What decisions did you make?", "API work mentioned"),
            "database":    ("How have you optimised database performance in your projects?", "Database work mentioned"),
            "project":     ("Tell me about your most impactful project and your role in it.", "Projects in resume"),
            "internship":  ("What was your biggest achievement during your internship?", "Internship mentioned"),
            "team":        ("Describe a time you collaborated with a team to solve a technical problem.", "Team experience mentioned"),
        }

        for keyword, (question, reason) in skill_map.items():
            if keyword in text_lower and len(questions) < num_questions:
                questions.append({"question": question, "reason": reason})

        # Fill remaining with role-based questions
        topics = self._pick_topic(role)
        bank_q = self._generate_from_bank(difficulty, topics)
        while len(questions) < num_questions:
            q = self._generate_from_bank(difficulty, self._pick_topic(role))
            questions.append({"question": q["question"], "reason": f"Common {role} interview question"})

        return questions[:num_questions]
    