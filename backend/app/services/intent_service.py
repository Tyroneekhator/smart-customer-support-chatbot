import json
import random
import os
import re
from typing import Dict, Any, List


class IntentService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        intents_path = os.path.join(base_dir, "data", "intents.json")

        with open(intents_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def clean_message(self, message: str) -> str:
        cleaned = message.lower().strip()
        cleaned = re.sub(r"[^\w\s]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def get_response_by_tag(self, tag: str) -> Dict[str, Any]:
        for intent in self.data["intents"]:
            if intent["tag"] == tag:
                return {
                    "intent": intent["tag"],
                    "reply": random.choice(intent["responses"])
                }

        return {
            "intent": "fallback",
            "reply": "I am sorry, I did not understand that."
        }

    def keyword_score(self, cleaned_message: str, keywords: List[str]) -> int:
        score = 0

        for keyword in keywords:
            cleaned_keyword = self.clean_message(keyword)

            if cleaned_keyword in cleaned_message:
                if " " in cleaned_keyword:
                    score += 3
                else:
                    score += 1

        return score

    def detect_intent(self, message: str) -> Dict[str, Any]:
        cleaned_message = self.clean_message(message)

        if not cleaned_message:
            return {
                "intent": "empty_message",
                "reply": "Please enter a message so I can help you."
            }

        priority_intents = [
            "cancel_order",
            "confirm_order",
            "price",
            "opening_hours",
            "delivery",
            "contact",
            "complaint"
        ]

        best_intent = None
        best_score = 0

        for tag in priority_intents:
            intent = self.find_intent_by_tag(tag)

            if not intent:
                continue

            score = self.keyword_score(cleaned_message, intent["keywords"])

            if score > best_score:
                best_score = score
                best_intent = intent

        if best_intent and best_score > 0:
            return {
                "intent": best_intent["tag"],
                "reply": random.choice(best_intent["responses"])
            }

        for intent in self.data["intents"]:
            score = self.keyword_score(cleaned_message, intent["keywords"])

            if score > best_score:
                best_score = score
                best_intent = intent

        if best_intent and best_score > 0:
            return {
                "intent": best_intent["tag"],
                "reply": random.choice(best_intent["responses"])
            }

        return {
            "intent": "fallback",
            "reply": (
                "I am sorry, I did not understand that. "
                "You can ask me about our menu, prices, opening hours, delivery, contact details, or placing an order."
            )
        }

    def find_intent_by_tag(self, tag: str):
        for intent in self.data["intents"]:
            if intent["tag"] == tag:
                return intent

        return None