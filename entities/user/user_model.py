from mongoengine import Document, StringField, FloatField, ListField,IntField, EmbeddedDocument, EmbeddedDocumentField, ReferenceField, BooleanField

from ..chat.chat_model import Chat

class User(Document):
    user_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    chats = ListField(EmbeddedDocumentField(Chat))

    # ✅ Personal Info
    gender = StringField(choices=["male", "female", "gay", "other"])  # restrict values
    preferred_gender = StringField(choices=["male", "female", "gay", "other"])
    age = IntField(min_value=0)

    # ✅ Location Fields
    city = StringField()
    state = StringField()
    country_code = StringField()
    latitude = FloatField()
    longitude = FloatField()

    open_to_flowers = BooleanField(default=True)
    is_familiar = BooleanField(default=False)

    def to_json(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "preferred_gender":self.preferred_gender,
            "chats": [chat.to_json() for chat in self.chats],
            "location": {
                "city": self.city,
                "state": self.state,
                "country_code": self.country_code,
                "lat": self.latitude,
                "lon": self.longitude,
            },
            "is_familiar":self.is_familiar
        }