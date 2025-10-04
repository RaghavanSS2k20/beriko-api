from mongoengine import Document, EmbeddedDocument, fields
import datetime


class Message(EmbeddedDocument):
    sender = fields.StringField(required=True)   # user_id of sender
    content = fields.StringField(required=True)        # message content
    timestamp = fields.DateTimeField(default=datetime.datetime.utcnow)
    # status = fields.StringField(choices=["sent", "delivered", "read"], default="sent")


class Conversation(Document):
    participants = fields.ListField(fields.StringField(), required=True)  
    messages = fields.EmbeddedDocumentListField(Message)
    last_message = fields.StringField()   # quick access for list screens
    updated_at = fields.DateTimeField(default=datetime.timezone.utc)

    meta = {
        "indexes": [
            {"fields": ["participants"], "unique": True},
            "-updated_at"
        ]
    }
