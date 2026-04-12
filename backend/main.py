"""
main.py  -  AI Interview Preparation Platform (UPGRADED Backend)
FastAPI Backend with all endpoints:
  - /generate-question
  - /evaluate-answer  (returns followup_question)
  - /resume-questions
  - /performance/:username
  - /leaderboard
  - /reset/:username
  - /health

Run: uvicorn main:app --reload --port 8000
Set:  export OPENAI_API_KEY=your_key_here
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3, json, os, random
from datetime import datetime

# ── OpenAI (optional) ─────────────────────────────────────────────────────────
try:
    import openai
    OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
    if OPENAI_KEY:
        openai.api_key = OPENAI_KEY
        AI_AVAILABLE = True
    else:
        AI_AVAILABLE = False
        print("⚠️  OPENAI_API_KEY not set — using rule-based evaluation.")
except ImportError:
    AI_AVAILABLE = False

# ── NLP libs (optional) ───────────────────────────────────────────────────────
try:
    import spacy
    nlp_model = spacy.load("en_core_web_sm")
    SPACY_OK = True
except Exception:
    SPACY_OK = False

try:
    import nltk
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt",     quiet=True)
    nltk.download("punkt_tab", quiet=True)
    NLTK_OK = True
except Exception:
    NLTK_OK = False

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="InterviewAI Pro API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = "interview_platform.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL,
            question  TEXT    NOT NULL,
            answer    TEXT    NOT NULL,
            score     REAL    NOT NULL,
            grade     TEXT,
            feedback  TEXT,
            role      TEXT,
            topic     TEXT,
            timestamp TEXT    NOT NULL
        )
    """)
    conn.commit(); conn.close()

init_db()

# ── Question Bank ─────────────────────────────────────────────────────────────
QUESTION_BANK = {
    "Software Developer": {
        "DSA": {
            "Easy": [
                {"question": "What is the time complexity of binary search and why?",
                 "hint": "Think about how many times you can halve n."},
                {"question": "Explain the difference between a stack and a queue with examples.",
                 "hint": "LIFO vs FIFO — think undo history vs print queue."},
                {"question": "What is a linked list and when would you prefer it over an array?",
                 "hint": "Consider insertion/deletion performance."},
                {"question": "What is a hash table and how does it handle collisions?",
                 "hint": "Chaining or open addressing."},
                {"question": "Explain the difference between recursion and iteration.",
                 "hint": "Call stack, base case, performance trade-offs."},
            ],
            "Medium": [
                {"question": "Explain how merge sort works and state its time and space complexity.",
                 "hint": "Divide and conquer — O(n log n) time, O(n) space."},
                {"question": "What is dynamic programming? Give a classic example.",
                 "hint": "Overlapping subproblems + optimal substructure. Think Fibonacci or knapsack."},
                {"question": "Explain the difference between BFS and DFS and when to use each.",
                 "hint": "Queue vs stack. Shortest path vs connectivity."},
                {"question": "What is a binary search tree? What are its average-case complexities?",
                 "hint": "O(log n) for balanced trees."},
            ],
            "Hard": [
                {"question": "How would you find the shortest path between two nodes in a large weighted graph?",
                 "hint": "Dijkstra's or A* algorithm. Discuss priority queue."},
                {"question": "Explain how a red-black tree maintains balance. Why is this important?",
                 "hint": "Colour rules and rotations. Guarantees O(log n) operations."},
            ],
        },
        "DBMS": {
            "Easy": [
                {"question": "What is the difference between SQL and NoSQL databases?",
                 "hint": "Schema, scalability, ACID vs BASE."},
                {"question": "What are ACID properties? Why do they matter?",
                 "hint": "Atomicity, Consistency, Isolation, Durability."},
                {"question": "What is a primary key and a foreign key?",
                 "hint": "Uniqueness and referential integrity."},
            ],
            "Medium": [
                {"question": "Explain database indexing. When should you add an index and when should you avoid it?",
                 "hint": "Read performance vs write overhead."},
                {"question": "What is database normalisation? Explain 1NF, 2NF, 3NF.",
                 "hint": "Eliminating redundancy at each level."},
                {"question": "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?",
                 "hint": "Think about which rows are included."},
            ],
            "Hard": [
                {"question": "Design a database schema for a social media platform like Twitter.",
                 "hint": "Users, posts, followers, likes, hashtags — think about scale."},
                {"question": "Explain transaction isolation levels and the problems each solves.",
                 "hint": "Dirty read, non-repeatable read, phantom read."},
            ],
        },
        "OS": {
            "Easy": [
                {"question": "What is the difference between a process and a thread?",
                 "hint": "Memory isolation vs sharing."},
                {"question": "What is virtual memory and why is it useful?",
                 "hint": "Extends RAM using disk — paging and page tables."},
            ],
            "Medium": [
                {"question": "Explain deadlock and the four Coffman conditions required for it.",
                 "hint": "Mutual exclusion, hold-and-wait, no preemption, circular wait."},
                {"question": "How does CPU scheduling work? Compare FCFS, Round Robin, and Priority scheduling.",
                 "hint": "Throughput, response time, fairness trade-offs."},
            ],
            "Hard": [
                {"question": "How does a modern OS handle page faults from start to finish?",
                 "hint": "TLB miss → page table walk → disk swap → update TLB."},
            ],
        },
        "HR": {
            "Easy": [
                {"question": "Tell me about yourself.",
                 "hint": "Past (education/experience), present (current role), future (goals). 2 minutes."},
                {"question": "Why do you want to work here?",
                 "hint": "Research the company mission, tech stack, and culture. Align with your goals."},
                {"question": "What are your greatest strengths?",
                 "hint": "Pick 2–3 strengths backed by real examples."},
                {"question": "Where do you see yourself in 5 years?",
                 "hint": "Show ambition aligned with company growth."},
                {"question": "Why are you leaving your current job?",
                 "hint": "Stay positive — focus on growth opportunities, not complaints."},
            ],
            "Medium": [
                {"question": "Tell me about a time you failed and what you learned from it.",
                 "hint": "STAR method. Be honest about the failure and emphasise the learning."},
                {"question": "Describe a situation where you had to work with a difficult team member.",
                 "hint": "STAR method. Show communication and empathy skills."},
                {"question": "Tell me about a project you are most proud of.",
                 "hint": "Highlight your individual impact and technical decisions."},
                {"question": "How do you handle tight deadlines and pressure?",
                 "hint": "Give a real example with your prioritisation strategy."},
            ],
            "Hard": [
                {"question": "Describe a time you had to make a critical decision with incomplete information.",
                 "hint": "Show your decision-making framework and how you managed risk."},
                {"question": "Tell me about a time you led a team through a major technical challenge.",
                 "hint": "Leadership, communication, technical ownership, measurable outcome."},
                {"question": "Describe a situation where you disagreed with your manager. How did you handle it?",
                 "hint": "Show respectful assertiveness and professional resolution."},
            ],
        },
        "System Design": {
            "Easy": [
                {"question": "What is the difference between horizontal and vertical scaling?",
                 "hint": "More machines vs a bigger machine. Cost and limits of each."},
            ],
            "Medium": [
                {"question": "How would you design a URL shortener like bit.ly?",
                 "hint": "Hashing, database schema, redirect logic, analytics."},
                {"question": "Design a rate limiter. What algorithms would you use?",
                 "hint": "Token bucket, leaky bucket, sliding window counter."},
            ],
            "Hard": [
                {"question": "Design a distributed caching system. How would you handle cache invalidation?",
                 "hint": "Eviction policies, replication, consistency vs availability."},
                {"question": "How would you design a real-time chat application for millions of users?",
                 "hint": "WebSockets, message queues, horizontal scaling, presence."},
                {"question": "Design a news feed system like Facebook's. How do you handle fan-out?",
                 "hint": "Push vs pull model. Ranking, caching, celebrity accounts."},
            ],
        },
    },
    "Frontend Developer": {
        "React": {
            "Easy": [
                {"question": "What is the virtual DOM and why does React use it?",
                 "hint": "Reconciliation and diffing algorithm."},
                {"question": "Explain the difference between props and state in React.",
                 "hint": "External/immutable vs internal/mutable."},
            ],
            "Medium": [
                {"question": "Explain React hooks. What problems do they solve?",
                 "hint": "useState, useEffect, custom hooks. Replacing class components."},
                {"question": "What is the Context API and when would you use it over Redux?",
                 "hint": "Scope of state sharing. Complexity vs boilerplate trade-off."},
                {"question": "Explain React's reconciliation algorithm.",
                 "hint": "Diffing with keys. When components re-render."},
            ],
            "Hard": [
                {"question": "How would you optimise a React application with slow rendering?",
                 "hint": "useMemo, useCallback, React.memo, code splitting, lazy loading."},
            ],
        },
        "CSS": {
            "Easy": [
                {"question": "Explain the CSS box model.",
                 "hint": "Content → padding → border → margin."},
                {"question": "What is the difference between Flexbox and CSS Grid?",
                 "hint": "1D (rows/columns) vs 2D layouts."},
            ],
            "Medium": [
                {"question": "How does CSS specificity work? Give the order.",
                 "hint": "Inline > ID > class/pseudo-class > element."},
                {"question": "What is the difference between em, rem, vw, and px units?",
                 "hint": "Relative vs absolute. Parent vs root."},
            ],
            "Hard": [
                {"question": "How would you build a fully responsive design without a CSS framework?",
                 "hint": "Media queries, fluid grids, relative units, container queries."},
            ],
        },
        "HR": {
            "Easy": [
                {"question": "Tell me about yourself.", "hint": "Past, present, future — 2 minutes."},
                {"question": "Why do you want to be a frontend developer?",
                 "hint": "Show passion for UI/UX and user experience."},
            ],
            "Medium": [
                {"question": "Describe your most challenging frontend project.",
                 "hint": "Highlight technical problem-solving and creativity."},
            ],
            "Hard": [
                {"question": "Tell me about a UI decision you made that significantly improved user engagement.",
                 "hint": "Quantify the impact. Show data-driven thinking."},
            ],
        },
    },
    "Data Scientist": {
        "ML": {
            "Easy": [
                {"question": "What is the difference between supervised and unsupervised learning?",
                 "hint": "Labelled vs unlabelled data."},
                {"question": "Explain overfitting and three ways to prevent it.",
                 "hint": "Regularisation, cross-validation, dropout, more data."},
            ],
            "Medium": [
                {"question": "Explain the bias-variance trade-off in machine learning.",
                 "hint": "Complex models overfit, simple models underfit."},
                {"question": "How does gradient descent work? What are its variants?",
                 "hint": "Batch, stochastic, mini-batch. Learning rate impact."},
                {"question": "What is cross-validation and why is it important?",
                 "hint": "k-fold. Generalisation vs overfitting detection."},
            ],
            "Hard": [
                {"question": "Explain how a transformer model works. What is the attention mechanism?",
                 "hint": "Self-attention, Q/K/V matrices, positional encoding."},
            ],
        },
        "Statistics": {
            "Easy": [
                {"question": "What is the difference between mean, median, and mode?",
                 "hint": "Central tendency. Which is robust to outliers?"},
            ],
            "Medium": [
                {"question": "Explain p-value and statistical significance.",
                 "hint": "Probability of observing results under the null hypothesis."},
                {"question": "What is the Central Limit Theorem and why is it fundamental?",
                 "hint": "Sampling distributions converge to normal as n increases."},
            ],
            "Hard": [
                {"question": "How would you design an A/B test for a new recommendation algorithm?",
                 "hint": "Sample size, power, control group, metric selection, duration."},
            ],
        },
        "HR": {
            "Easy": [
                {"question": "Tell me about yourself.", "hint": "Past, present, future — 2 minutes."},
                {"question": "What drew you to data science?",
                 "hint": "Show genuine curiosity for data and measurable insights."},
            ],
            "Medium": [
                {"question": "Describe a data project that had a real business impact.",
                 "hint": "Quantify the impact — revenue, cost saving, efficiency gain."},
            ],
            "Hard": [
                {"question": "Tell me about a time you had to explain a complex model to a non-technical stakeholder.",
                 "hint": "Simplification, analogies, focusing on business value not math."},
            ],
        },
    },
}

ROLES = list(QUESTION_BANK.keys())

# ── NLP Keywords ──────────────────────────────────────────────────────────────
TECH_KEYWORDS = [
    "algorithm","complexity","efficient","optimize","data structure","implement",
    "approach","solution","example","case","scenario","experience","project",
    "team","problem","result","outcome","performance","scalable","database",
    "thread","process","memory","cache","index","query","api","framework",
    "testing","debugging","deploy","architecture","design","pattern","principle",
    "agile","scrum","sprint","deadline","communication","leadership","challenge",
    "responsibility","impact","learn","improve","collaborate","mentor","review",
    "function","class","object","variable","loop","recursion","iteration",
    "hash","tree","graph","stack","queue","array","list","dictionary",
]

# ── Pydantic Models ───────────────────────────────────────────────────────────
class QuestionRequest(BaseModel):
    role:       str
    difficulty: str
    topic:      Optional[str] = None

class EvaluateRequest(BaseModel):
    question: str
    answer:   str
    role:     str
    username: str

class ResumeRequest(BaseModel):
    resume_text:   str
    role:          str
    difficulty:    str
    num_questions: int = 5

# ── Helpers ───────────────────────────────────────────────────────────────────
def score_to_grade(score: float) -> str:
    if score >= 9:   return "A"
    if score >= 7.5: return "B"
    if score >= 6:   return "C"
    if score >= 4:   return "D"
    return "F"

def compute_nlp_metrics(answer: str) -> dict:
    words = answer.lower().split()
    wc    = len(words)
    kh    = sum(1 for w in words if w.strip(".,!?") in TECH_KEYWORDS)
    sents = [s.strip() for s in answer.replace("?","!").split(".") if s.strip()]
    return {
        "word_count":       wc,
        "keyword_hits":     kh,
        "sentence_count":   len(sents),
        "avg_sentence_len": round(wc / max(len(sents), 1), 1),
    }

def rule_based_evaluate(question: str, answer: str, role: str) -> dict:
    nlp   = compute_nlp_metrics(answer)
    wc, kh = nlp["word_count"], nlp["keyword_hits"]
    score = 5.0
    strengths, improvements = [], []

    # Length
    if wc >= 80:
        score += 1.5; strengths.append("Detailed and comprehensive — good answer length.")
    elif wc >= 40:
        score += 0.5; strengths.append("Reasonable answer length.")
    else:
        score -= 1.0; improvements.append("Too short — aim for at least 50 words.")

    # Keywords
    if kh >= 5:
        score += 1.5; strengths.append("Excellent use of relevant technical vocabulary.")
    elif kh >= 2:
        score += 0.5; strengths.append("Some relevant keywords included.")
    else:
        improvements.append("Include more technical terms relevant to the question.")

    # STAR for HR
    q_lower = question.lower()
    is_hr   = any(w in q_lower for w in ["time you","describe","tell me","experience","situation","when you"])
    if is_hr:
        star_hits = sum(1 for w in ["situation","task","action","result","outcome","because","therefore","as a result"]
                        if w in answer.lower())
        if star_hits >= 3:
            score += 1.0; strengths.append("Good STAR method structure detected.")
        else:
            improvements.append("Use the STAR method: Situation → Task → Action → Result.")

    # Examples
    if any(p in answer.lower() for p in ["example","for instance","such as","like when","in my","at my","once i","i was working"]):
        score += 0.5; strengths.append("Good use of a specific real example.")
    else:
        improvements.append("Add a concrete personal example to strengthen your answer.")

    # Numbers / quantification
    if any(c.isdigit() for c in answer):
        score += 0.5; strengths.append("Quantified impact with numbers — impressive.")

    score = max(1.0, min(10.0, round(score, 1)))
    grade = score_to_grade(score)

    feedback_map = {
        "A": "Excellent answer! Well-structured, detailed, and insightful.",
        "B": "Good answer. A bit more depth and examples would make it excellent.",
        "C": "Decent attempt. Focus more on structure and technical specifics.",
        "D": "Needs significant improvement in detail, structure, and relevance.",
        "F": "Please review this topic and attempt with greater depth.",
    }
    ideal_map = {
        "what":    "A strong answer would include: a clear definition, a real-world example, trade-offs, and a personal connection.",
        "explain": "Start with the concept definition, then an analogy, then a practical example.",
        "how":     "Describe the step-by-step process, explain why each step matters, and mention edge cases.",
        "tell":    "Use STAR: Situation → Task → Action → Result (with measurable outcome).",
        "describe":"Use STAR: Situation → Task → Action → Result (with measurable outcome).",
        "design":  "Requirements → high-level architecture → deep-dive on critical components → trade-offs.",
        "why":     "Explain the core reasoning, give a real example, and connect it to your experience.",
    }
    q_first    = (question.lower().split()[0] if question else "what").strip("?.,")
    ideal      = ideal_map.get(q_first, ideal_map["what"])

    if not strengths:    strengths    = ["Attempted the question."]
    if not improvements: improvements = ["Add more detail and specific examples."]

    return {
        "score":            score,
        "grade":            grade,
        "strengths":        strengths[:3],
        "improvements":     improvements[:3],
        "feedback_summary": feedback_map.get(grade, "Keep practising!"),
        "ideal_answer":     ideal,
        "nlp_metrics":      nlp,
    }

def ai_evaluate(question: str, answer: str, role: str) -> dict:
    if not AI_AVAILABLE:
        return rule_based_evaluate(question, answer, role)
    nlp = compute_nlp_metrics(answer)
    try:
        prompt = f"""You are an expert technical interviewer evaluating a candidate for a {role} position.

Question: {question}
Candidate's Answer: {answer}

Evaluate and respond ONLY with a valid JSON object (no markdown, no explanation):
{{
  "score": <number 1-10>,
  "grade": <"A","B","C","D" or "F">,
  "strengths": [<up to 3 specific strengths as strings>],
  "improvements": [<up to 3 actionable suggestions as strings>],
  "feedback_summary": "<one sentence overall feedback>",
  "ideal_answer": "<2-3 sentence model answer for this specific question>"
}}"""
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=600, temperature=0.3)
        raw  = resp.choices[0].message.content.strip()
        raw  = raw.replace("```json","").replace("```","").strip()
        data = json.loads(raw)
        data["nlp_metrics"] = nlp
        return data
    except Exception as e:
        print(f"AI evaluate error: {e}")
        result = rule_based_evaluate(question, answer, role)
        result["nlp_metrics"] = nlp
        return result

def generate_followup(question: str, answer: str, role: str) -> Optional[str]:
    # Rule-based fallbacks
    q = question.lower()
    rule_followups = {
        lambda q: "time you" in q or "tell me" in q:            "What would you do differently if you faced the same situation today?",
        lambda q: "design" in q or "system" in q:               "How would your design change if traffic increased by 100x overnight?",
        lambda q: "algorithm" in q or "complexity" in q:        "Can you also walk me through the space complexity of your solution?",
        lambda q: "strength" in q:                              "Can you give one more example where that strength helped you overcome a major obstacle?",
        lambda q: "weakness" in q or "fail" in q or "mistake" in q: "What concrete steps have you taken since then to improve?",
        lambda q: "database" in q or "sql" in q:                "How would you optimise this query if the table had 500 million rows?",
        lambda q: "scale" in q or "distributed" in q:           "How would you handle partial failures in this distributed system?",
    }
    if not AI_AVAILABLE:
        for condition, followup in rule_followups.items():
            if condition(q):
                return followup
        return "Can you elaborate further with a specific example from your experience?"

    try:
        prompt = f"""You are a strict technical interviewer for a {role} role.
The candidate was asked: "{question}"
They answered: "{answer}"

Ask ONE sharp follow-up question that probes a gap or interesting point in their answer.
Make it sound natural — one sentence, no preamble."""
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=80, temperature=0.7)
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Can you elaborate further with a specific example from your experience?"

def ai_generate_question(role: str, difficulty: str, topic: Optional[str]) -> Optional[dict]:
    if not AI_AVAILABLE:
        return None
    try:
        tstr = f"related to {topic}" if topic else "relevant to the role"
        prompt = f"""Generate a single technical interview question for a {role} at {difficulty} level, {tstr}.
Respond ONLY with a valid JSON object:
{{"question":"<question>","hint":"<brief hint>","topic":"<topic category>"}}"""
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=200, temperature=0.8)
        raw  = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        data = json.loads(raw)
        data["source"] = "ai"
        return data
    except Exception:
        return None

def ai_resume_questions(resume_text: str, role: str, difficulty: str, num_questions: int) -> List[dict]:
    if not AI_AVAILABLE:
        return [
            {"question": f"Tell me about your most significant project and the technical challenges you faced.",
             "reason": "Derived from your experience section.", "topic": "General"}
            for _ in range(min(num_questions, 3))
        ]
    try:
        prompt = f"""You are an expert interviewer. Analyse this resume and generate {num_questions} targeted interview questions for a {role} position at {difficulty} level.

Resume:
{resume_text[:3000]}

Respond ONLY with a valid JSON array (no markdown):
[{{"question":"<specific question>","reason":"<why — reference actual resume content>","topic":"<topic>"}}]

Make each question specific to actual skills, projects, or experience in the resume."""
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=1400, temperature=0.7)
        raw  = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"Resume questions error: {e}")
        return [{"question":"Tell me about your most significant project.","reason":"From your resume.","topic":"General"}]

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "InterviewAI Pro API v2.0.0", "status": "running", "ai": AI_AVAILABLE}

@app.get("/roles")
def get_roles():
    return {"roles": ROLES}

@app.get("/topics")
def get_topics(role: str):
    return {"topics": list(QUESTION_BANK.get(role, {}).keys())}

@app.post("/generate-question")
def generate_question(req: QuestionRequest):
    if req.role not in QUESTION_BANK:
        raise HTTPException(404, f"Role '{req.role}' not found.")

    role_bank  = QUESTION_BANK[req.role]
    topic_pool = {req.topic: role_bank[req.topic]} if (req.topic and req.topic in role_bank) else role_bank

    candidates = []
    for topic_name, diff_map in topic_pool.items():
        for q in diff_map.get(req.difficulty, []):
            candidates.append({**q, "topic": topic_name, "source": "bank"})

    # 40% chance of AI-generated question
    if (random.random() < 0.4) or not candidates:
        ai_q = ai_generate_question(req.role, req.difficulty, req.topic)
        if ai_q:
            return ai_q

    if not candidates:
        raise HTTPException(404, "No questions found for these criteria.")
    return random.choice(candidates)

@app.post("/evaluate-answer")
def evaluate_answer(req: EvaluateRequest):
    if not req.answer.strip():
        raise HTTPException(400, "Answer cannot be empty.")

    result   = ai_evaluate(req.question, req.answer, req.role)
    followup = generate_followup(req.question, req.answer, req.role)
    result["followup_question"] = followup

    # Persist to DB
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO sessions (username,question,answer,score,grade,feedback,role,topic,timestamp)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (req.username, req.question, req.answer, result["score"],
              result.get("grade",""), result.get("feedback_summary",""),
              req.role, "", datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit(); conn.close()
    except Exception as e:
        print(f"DB error: {e}")

    return result

@app.post("/resume-questions")
def resume_questions(req: ResumeRequest):
    if not req.resume_text.strip():
        raise HTTPException(400, "Resume text cannot be empty.")
    questions = ai_resume_questions(req.resume_text, req.role, req.difficulty, req.num_questions)
    return {"questions": questions}

@app.get("/performance/{username}")
def get_performance(username: str):
    try:
        conn = get_db()
        rows = conn.execute("""
            SELECT score, grade, role, topic, timestamp, feedback
            FROM sessions WHERE username=? ORDER BY id DESC LIMIT 50
        """, (username,)).fetchall()
        conn.close()

        if not rows:
            return {"total_sessions":0,"average_score":0,"best_score":0,
                    "history":[],"role_breakdown":{}}

        history = [dict(r) for r in rows]
        scores  = [h["score"] for h in history]
        role_scores = {}
        for h in history:
            r = h["role"] or "Unknown"
            role_scores.setdefault(r,[]).append(h["score"])
        role_breakdown = {r: round(sum(v)/len(v),1) for r,v in role_scores.items()}

        return {
            "total_sessions": len(history),
            "average_score":  round(sum(scores)/len(scores),1),
            "best_score":     max(scores),
            "history":        history,
            "role_breakdown": role_breakdown,
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/leaderboard")
def get_leaderboard():
    try:
        conn = get_db()
        rows = conn.execute("""
            SELECT username,
                   ROUND(AVG(score),1) AS avg_score,
                   COUNT(*)            AS sessions,
                   MAX(score)          AS best_score
            FROM sessions
            GROUP BY username
            HAVING sessions >= 3
            ORDER BY avg_score DESC
            LIMIT 15
        """).fetchall()
        conn.close()
        return {"leaderboard": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.delete("/reset/{username}")
def reset_history(username: str):
    try:
        conn = get_db()
        conn.execute("DELETE FROM sessions WHERE username=?", (username,))
        conn.commit(); conn.close()
        return {"message": f"History cleared for {username}"}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/health")
def health():
    return {
        "status":       "healthy",
        "ai_available": AI_AVAILABLE,
        "spacy":        SPACY_OK,
        "nltk":         NLTK_OK,
        "db":           os.path.exists(DB_PATH),
    }
