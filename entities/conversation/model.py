from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime
from slugify import slugify


class Message(EmbeddedDocument):
    sender = fields.StringField(required=True)   # user_id of sender
    content = fields.StringField(required=True)        # message content
    timestamp = fields.DateTimeField(default=datetime.utcnow())
    # status = fields.StringField(choices=["sent", "delivered", "read"], default="sent")


class Conversation(Document):
    participants = fields.StringField(required=True , unique=True)
    messages = fields.EmbeddedDocumentListField(Message)
    last_message = fields.StringField()   # quick access for list screens
    updated_at = fields.DateTimeField(default=datetime.utcnow())

    meta = {
        "indexes": [
            # {"fields": ["participants"], "unique": True},
            "-updated_at"
        ]
    }

    def clean(self):
        if isinstance(self.participants, list):
            # sort and slugify with _ as separator
            self.participants = slugify("_".join(sorted(self.participants)), separator="_")
