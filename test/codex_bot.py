"""
codex_bot.py - a small chatbot that reads everything from hit_codex.json

Run:   python codex_bot.py          (chat)
       python codex_bot.py --demo   (shows sample questions and answers)

No extra libraries needed. To change what the bot knows, edit hit_codex.json.
"""

import json
import re
import sys
from pathlib import Path

CODEX_PATH = Path(__file__).with_name("hit_codex.json")


def load_codex(path=CODEX_PATH):
    """Read the JSON file and return it as a Python dictionary."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def has_word(text, word):
    """True if `word` (or phrase) appears in `text` as a whole word."""
    pattern = r"(?<!\w)" + re.escape(word.lower()) + r"(?!\w)"
    return re.search(pattern, text) is not None


def score(text, keywords):
    """How many of the keywords appear in the text."""
    return sum(1 for k in keywords if has_word(text, k))


class CodexBot:
    def __init__(self, codex):
        self.codex = codex
        self.safety = codex["safety"]
        self.style = codex["conversation_style"]
        self.mind = codex["emotions_and_mind"]
        self.shop = codex["shop_chatbot"]
        self.learning_faq = codex["self_build"]["faq"]

    # ----- help text -------------------------------------------------
    def help_text(self):
        return (
            "I can talk about:\n"
            "  - Feelings and the inner mind: anger, desire, greed, pride, envy,\n"
            "    attachment, overthinking, ego, stress, tiredness, motivation\n"
            "  - Learning plan: roadmap, timetable, videos, git tag, commit, API key\n"
            "  - Maa Khodal Cutlery Shop: delivery, products, location, contact, return\n"
            "Type 'quit' to stop."
        )

    # ----- main logic ------------------------------------------------
    def reply(self, message):
        text = message.lower().strip()

        if not text:
            return "Please type something and I will try to help."

        if text in ("help", "topics", "menu"):
            return self.help_text()

        if text in ("hi", "hello", "hey", "namaste", "hii"):
            return self.style["greetings"][0]

        if text in ("bye", "goodbye", "thanks", "thank you"):
            return self.style["goodbye"]

        # 1. Safety always comes first.
        if score(text, self.safety["crisis_keywords"]) > 0:
            return self.safety["crisis_reply"]

        # 2. Collect candidate answers from every part of the codex.
        candidates = []  # (score, priority, reply)

        for item in self.shop["faq"]:
            s = score(text, item["keywords"])
            if s:
                candidates.append((s, 3, item["answer"]))

        for item in self.learning_faq:
            s = score(text, item["keywords"])
            if s:
                candidates.append((s, 2, item["answer"]))

        mind_items = (
            self.mind["shadripu"]
            + self.mind["antahkarana"]
            + self.mind["general_emotions"]
        )
        for item in mind_items:
            s = score(text, item["keywords"])
            if s:
                candidates.append((s, 4, item["reply"]))

        # 3. Choose the best one: highest score, then highest priority.
        if candidates:
            candidates.sort(key=lambda c: (c[0], c[1]), reverse=True)
            return candidates[0][2]

        return self.style["fallback"]


def run_demo(bot):
    samples = [
        "hello",
        "I am so angry with my friend",
        "I feel jealous of my classmate",
        "I keep overthinking everything",
        "I cannot start studying, I feel lazy",
        "what is a git tag?",
        "Do you give home delivery?",
        "what is the price of steel spoon?",
        "what are your shop timings",
        "I want to die",
        "blah blah",
    ]
    for s in samples:
        print(f"You: {s}")
        print(f"Bot: {bot.reply(s)}\n")


def main():
    codex = load_codex()
    bot = CodexBot(codex)

    if "--demo" in sys.argv:
        run_demo(bot)
        return

    print(f"{codex['codex_meta']['name']} v{codex['codex_meta']['version']}")
    print("Type 'help' for topics or 'quit' to stop.\n")
    print("Bot:", codex["conversation_style"]["greetings"][0])

    while True:
        try:
            message = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBot:", codex["conversation_style"]["goodbye"])
            break
        if message.strip().lower() in ("quit", "exit", "q"):
            print("Bot:", codex["conversation_style"]["goodbye"])
            break
        print("Bot:", bot.reply(message), "\n")


if __name__ == "__main__":
    main()