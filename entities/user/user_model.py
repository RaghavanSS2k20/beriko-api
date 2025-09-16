from mongoengine import Document, StringField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentField, ReferenceField

from ..chat.chat_model import Chat
class User(Document):
    user_id = StringField(required=True, unique=True)
    name =  StringField(required=True)
    chats = ListField(EmbeddedDocumentField(Chat))

    def to_json(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "chats": [chat.to_json() for chat in self.chats]
        }