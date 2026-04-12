"""
answer_evaluator.py
Evaluates user answers using:
  1. spaCy + NLTK for NLP-based scoring (keyword matching, fluency)
  2. OpenAI API for intelligent feedback (strengths, improvements, ideal answer)
"""

import os
import re
import string
from typing import Optional

# NLP imports
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False

# Download required NLTK data (silent)
for resource in ["punkt", "stopwords", "averaged_perceptron_tagger", "punkt_tab"]:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

# Use simple split instead of word_tokenize as fallback
try:
    from nltk.tokenize import word_tokenize, sent_tokenize
except:
    word_tokenize = lambda x: x.split()
    sent_tokenize = lambda x: x.split('.')

from openai import OpenAI

# ── Keyword Bank ───────────────────────────────────────────────────────────

KEYWORDS = {
    "Data Structures": [
        "array", "linked list", "stack", "queue", "tree", "graph",
        "hash", "heap", "complexity", "node", "pointer", "index",
    ],
    "Algorithms": [
        "sort", "search", "complexity", "O(n)", "O(log n)", "recursion",
        "iteration", "divide", "conquer", "dynamic", "greedy",
    ],
    "Python": [
        "list", "dict", "tuple", "class", "function", "lambda",
        "decorator", "generator", "iterator", "exception", "module",
    ],
    "SQL": [
        "select", "join", "index", "primary key", "foreign key",
        "aggregate", "group by", "having", "subquery", "transaction",
    ],
    "Machine Learning": [
        "model", "training", "overfitting", "underfitting", "accuracy",
        "precision", "recall", "gradient", "epoch", "feature",
    ],
    "System Design": [
        "scalability", "load balancer", "cache", "database", "API",
        "microservices", "latency", "throughput", "availability",
    ],
    "Behavioral": [
        "team", "project", "challenge", "solution", "result",
        "learned", "improved", "collaborated", "managed", "delivered",
    ],
}


class AnswerEvaluator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    # ── Public API ─────────────────────────────────────────────────────────

    def evaluate(self, question: str, answer: str, role: str) -> dict:
        """
        Returns a full evaluation dict:
        {
            "score": int (0–10),
            "grade": str,
            "strengths": [str, ...],
            "improvements": [str, ...],
            "ideal_answer": str,
            "nlp_metrics": { word_count, sentence_count, keyword_hits, readability },
            "feedback_summary": str,
        }
        """
        if not answer or not answer.strip():
            return self._empty_answer_response()

        nlp_metrics = self._nlp_analysis(answer, question)
        nlp_score   = self._compute_nlp_score(answer, question, nlp_metrics)

        if self.client:
            try:
                ai_feedback = self._get_ai_feedback(question, answer, role, nlp_score)
                return ai_feedback
            except Exception:
                pass  # Fall back to NLP-only

        return self._nlp_only_feedback(answer, question, nlp_score, nlp_metrics)

    # ── NLP Analysis ───────────────────────────────────────────────────────

    def _nlp_analysis(self, answer: str, question: str) -> dict:
        clean   = answer.lower().translate(str.maketrans("", "", string.punctuation))
        tokens  = word_tokenize(clean)
        sents   = sent_tokenize(answer)
        stops   = set(stopwords.words("english"))
        content = [t for t in tokens if t not in stops and len(t) > 2]

        # Detect topic from question
        topic   = self._detect_topic(question)
        kw_list = KEYWORDS.get(topic, [])
        hits    = sum(1 for kw in kw_list if kw.lower() in clean)

        # spaCy entities (if available)
        entities = []
        if SPACY_AVAILABLE:
            doc      = nlp(answer[:1000])  # limit for speed
            entities = [ent.text for ent in doc.ents]

        return {
            "word_count":     len(tokens),
            "sentence_count": len(sents),
            "content_words":  len(content),
            "keyword_hits":   hits,
            "total_keywords": len(kw_list),
            "topic":          topic,
            "entities":       entities[:5],
        }

    def _compute_nlp_score(self, answer: str, question: str, metrics: dict) -> int:
        score = 0

        # 1. Length score (max 3 pts)
        wc = metrics["word_count"]
        if wc >= 100: score += 3
        elif wc >= 50: score += 2
        elif wc >= 20: score += 1

        # 2. Keyword coverage (max 4 pts)
        total = metrics["total_keywords"]
        hits  = metrics["keyword_hits"]
        if total > 0:
            ratio = hits / total
            score += round(ratio * 4)

        # 3. Sentence structure (max 2 pts)
        sc = metrics["sentence_count"]
        if sc >= 3: score += 2
        elif sc >= 2: score += 1

        # 4. Has examples or specifics (max 1 pt)
        example_phrases = ["for example", "such as", "like", "instance", "e.g", "specifically"]
        if any(p in answer.lower() for p in example_phrases):
            score += 1

        return min(score, 10)

    # ── AI Feedback ────────────────────────────────────────────────────────

    def _get_ai_feedback(self, question: str, answer: str, role: str, nlp_score: int) -> dict:
        prompt = f"""
You are an expert technical interviewer evaluating a candidate for a {role} position.

Question: {question}

Candidate's Answer: {answer}

NLP Analysis Score: {nlp_score}/10 (based on keyword coverage, length, and structure)

Please evaluate the answer and respond in the following JSON format ONLY (no extra text):
{{
  "score": <integer 0-10 that blends AI judgment with the NLP score>,
  "grade": "<A / B / C / D / F>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"],
  "ideal_answer": "<A concise model answer in 3-5 sentences>",
  "feedback_summary": "<One encouraging sentence of overall feedback>"
}}
"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.4,
        )
        import json
        raw  = response.choices[0].message.content.strip()
        data = json.loads(raw)

        # Inject NLP metrics for display
        data["nlp_metrics"] = {
            "word_count":    len(answer.split()),
            "keyword_hits":  self._nlp_analysis(answer, question)["keyword_hits"],
            "topic":         self._detect_topic(question),
        }
        return data

    # ── NLP-only Fallback ──────────────────────────────────────────────────

    def _nlp_only_feedback(self, answer: str, question: str, score: int, metrics: dict) -> dict:
        grade_map = {10: "A", 9: "A", 8: "B", 7: "B", 6: "C", 5: "C", 4: "D", 3: "D"}
        grade     = grade_map.get(score, "F")

        strengths, improvements = [], []

        if metrics["word_count"] >= 50:
            strengths.append("Good answer length with sufficient detail.")
        else:
            improvements.append("Try to write a longer, more detailed answer (aim for 50+ words).")

        if metrics["keyword_hits"] >= 3:
            strengths.append(f"Used {metrics['keyword_hits']} relevant technical keywords.")
        else:
            improvements.append("Include more technical keywords related to the topic.")

        if metrics["sentence_count"] >= 3:
            strengths.append("Answer is well-structured with multiple sentences.")
        else:
            improvements.append("Break your answer into more structured sentences or points.")

        example_phrases = ["for example", "such as", "like", "instance", "e.g"]
        if any(p in answer.lower() for p in example_phrases):
            strengths.append("Good use of examples to support your answer.")
        else:
            improvements.append("Add a concrete example to strengthen your explanation.")

        if not strengths:
            strengths = ["You attempted to answer the question — that's a start!"]

        return {
            "score":            score,
            "grade":            grade,
            "strengths":        strengths[:2],
            "improvements":     improvements[:2],
            "ideal_answer":     "Enable the OpenAI API key to see model answers.",
            "feedback_summary": f"Score {score}/10 — keep practising and focus on the improvements above.",
            "nlp_metrics":      metrics,
        }

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _detect_topic(question: str) -> str:
        q = question.lower()
        mapping = {
            "Data Structures": ["array", "linked list", "stack", "queue", "tree", "heap", "hash"],
            "Algorithms":      ["sort", "search", "complexity", "algorithm", "recursion"],
            "Python":          ["python", "list", "dictionary", "decorator", "generator"],
            "SQL":             ["sql", "database", "query", "join", "index", "table"],
            "Machine Learning":["model", "training", "neural", "classification", "regression"],
            "System Design":   ["design", "scale", "load", "api", "microservice", "cache"],
        }
        for topic, keywords in mapping.items():
            if any(kw in q for kw in keywords):
                return topic
        return "Behavioral"

    @staticmethod
    def _empty_answer_response() -> dict:
        return {
            "score":            0,
            "grade":            "F",
            "strengths":        [],
            "improvements":     ["Please provide an answer before submitting."],
            "ideal_answer":     "",
            "feedback_summary": "No answer was provided.",
            "nlp_metrics":      {},
        }
