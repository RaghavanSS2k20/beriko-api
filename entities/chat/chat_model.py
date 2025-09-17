from flask import Flask
from mongoengine import *
from datetime import datetime

class Chat(EmbeddedDocument):
     sender = StringField(required=True, choices=["user", "agent"])  # who sent the message
     content = StringField(required=True)
     timestamp = DateTimeField(default=datetime.utcnow)

     def to_json(self):
        return {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp  # already float epoch
        }

