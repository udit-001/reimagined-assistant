from .chatbot import Chatbot
from .persona import personas


class ChatSessionCache:
    def __init__(self):
        self.cache = {}

    def add_session(self, chatbot: Chatbot, user_id: str):
        self.cache[f"{user_id}:{chatbot.persona.name}"] = chatbot

    def session_exists(self, user_id: str):
        return True if user_id in self.cache else False

    def get_or_create_session(self, user_id: str, persona: str):
        if f"{user_id}:{persona}" in self.cache.keys():
            return self.cache[f"{user_id}:{persona}"]
        else:
            chatbot = Chatbot(persona=personas[persona], user_id=user_id)
            self.add_session(chatbot, user_id)
            return chatbot


CHATBOT_CACHE = ChatSessionCache()
