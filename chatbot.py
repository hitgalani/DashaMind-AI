
import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load your two JSON datasets
BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "data/chatbot_intent_dataset.json", "r", encoding="utf-8") as f:
    intent_data = json.load(f)

with open(BASE_DIR / "data/chatbot_data.json", "r", encoding="utf-8") as f:
    chatbot_data = json.load(f)


# Prepare intent examples
intent_texts = [item["text"] for item in intent_data]
intent_labels = [item["intent"] for item in intent_data]
intent_responses = [item["response"] for item in intent_data]

# Prepare question-answer examples
questions = [item["question"] for item in chatbot_data]
answers = [item["answer"] for item in chatbot_data]


# Create TF-IDF models
intent_vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    strip_accents="unicode"
)

question_vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    strip_accents="unicode"
)

intent_matrix = intent_vectorizer.fit_transform(intent_texts)
question_matrix = question_vectorizer.fit_transform(questions)


def clean_text(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def get_intent(user_message):
    user_message = clean_text(user_message)

    vector = intent_vectorizer.transform([user_message])
    scores = cosine_similarity(vector, intent_matrix)[0]

    best_index = scores.argmax()

    return {
        "intent": intent_labels[best_index],
        "response": intent_responses[best_index],
        "confidence": float(scores[best_index])
    }


def get_chatbot_answer(user_message):
    user_message = clean_text(user_message)

    # Find the closest question in chatbot_data.json
    vector = question_vectorizer.transform([user_message])
    scores = cosine_similarity(vector, question_matrix)[0]

    best_index = scores.argmax()
    best_score = float(scores[best_index])

    # Prefer an answer from the chatbot Q&A dataset
    if best_score >= 0.25:
        return answers[best_index]

    # If no close question is found, use intent recognition
    intent_result = get_intent(user_message)

    if intent_result["confidence"] >= 0.25:
        return intent_result["response"]

    return "I'm not sure I understand. Can you explain that differently?"


# Start chatbot
def start_chatbot():
    print("\n================================")
    print("       MY AI CHATBOT")
    print("================================")
    print("Type 'exit' to stop the chatbot.\n")

    while True:
        user_message = input("You: ").strip()

        if not user_message:
            continue

        if user_message.lower() in ["exit", "quit", "bye"]:
            print("Bot: Goodbye! Have a nice day.")
            break

        response = get_chatbot_answer(user_message)
        print("Bot:", response)


if __name__ == "__main__":
    start_chatbot()
