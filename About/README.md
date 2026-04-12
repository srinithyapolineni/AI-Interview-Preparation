# 🎤 AI Interview Preparation Platform

> An AI-powered mock interview system that generates role-specific questions,
> evaluates answers using NLP, and provides intelligent feedback with scoring.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-purple?logo=openai)
![spaCy](https://img.shields.io/badge/spaCy-3.7-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Problem Statement

Technical interviews are stressful. Most students practise alone with no
feedback. This platform uses AI + NLP to simulate real interviews, evaluate
answers, and guide improvement — like having a personal interview coach.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎲 Question Generation | AI-generated + curated questions across 7 roles & 3 difficulty levels |
| 🧠 NLP Analysis | Keyword matching, length scoring, and structure analysis using spaCy + NLTK |
| 🤖 AI Feedback | OpenAI GPT-powered strengths, improvements, and ideal answer |
| 📊 Dashboard | Track scores over time with role-wise performance breakdown |
| 🎯 Role-Based | Software Dev, Data Analyst, ML Engineer, and more |

---

## 🛠️ Tech Stack

```
Frontend    →  Streamlit (Python)
Backend     →  FastAPI + Uvicorn
AI Engine   →  OpenAI GPT-3.5-turbo
NLP         →  spaCy (en_core_web_sm) + NLTK
Database    →  SQLite (built-in, no setup required)
```

---

## 📂 Project Structure

```
ai-interview-platform/
│
├── backend/
│   ├── main.py                  # FastAPI routes
│   ├── question_generator.py    # Curated bank + OpenAI question generation
│   ├── answer_evaluator.py      # NLP scoring + AI feedback engine
│   └── database.py              # SQLite persistence layer
│
├── frontend/
│   └── app.py                   # Streamlit UI (Interview, Dashboard, About)
│
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-interview-platform.git
cd ai-interview-platform
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Set your OpenAI API key (optional but recommended)
```bash
# Linux / macOS
export OPENAI_API_KEY="sk-your-key-here"

# Windows
set OPENAI_API_KEY=sk-your-key-here
```
> ⚠️ Without the key, the platform still works using the curated question bank
> and NLP-only evaluation (no cost).

### 4. Start the backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Start the frontend (new terminal)
```bash
cd frontend
streamlit run app.py
```

### 6. Open in browser
```
http://localhost:8501
```

---

## 🎯 How It Works

```
User selects Role + Difficulty
         │
         ▼
Question Generator
  ├── OpenAI API  →  dynamic, role-specific question
  └── Local bank  →  fallback (150+ curated questions)
         │
         ▼
User writes answer
         │
         ▼
Answer Evaluator
  ├── spaCy + NLTK  →  keyword hits, length, structure score
  └── OpenAI API    →  strengths, improvements, ideal answer
         │
         ▼
Score (0–10) + Grade + Feedback
         │
         ▼
SQLite  →  Performance Dashboard
```

---

## 📊 Scoring System

| Component | Weight | How |
|---|---|---|
| Answer length | 30% | Penalises very short answers |
| Keyword coverage | 40% | Relevant technical terms detected |
| Sentence structure | 20% | Multi-sentence, well-formed responses |
| Examples used | 10% | Detects phrases like "for example", "such as" |

AI-powered scoring blends the NLP score with GPT's understanding for a
more holistic evaluation.

---

## 🖥️ Screenshots

> *(Add screenshots here after running the app)*

---

## 📈 Roadmap

- [ ] 🎤 Voice answer input using `speech_recognition`
- [ ] 📄 Resume upload → personalised questions
- [ ] 🧪 Coding challenge evaluation (LeetCode-style)
- [ ] 🌐 Deploy to Streamlit Cloud + Railway

---

## 💼 Resume Line

> **AI Interview Preparation Platform**
> Built a full-stack AI-powered mock interview system with a FastAPI backend and
> Streamlit frontend. Integrated OpenAI GPT-3.5 for intelligent feedback and
> spaCy + NLTK for NLP-based answer evaluation. Supports 7 roles, 3 difficulty
> levels, and persistent performance tracking via SQLite.
> *Technologies: Python · FastAPI · Streamlit · OpenAI API · spaCy · NLTK · SQLite*

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first.

---

*Built by a CSE student to make interview preparation smarter and more accessible.*