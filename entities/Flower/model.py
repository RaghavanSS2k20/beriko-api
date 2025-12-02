from mongoengine import (
    Document, StringField, ReferenceField, DateTimeField,
    BooleanField, EnumField, CASCADE
)
from datetime import datetime, timedelta


class Flower(Document):
    """
    Beriko Flower Model 🌸
    Represents an intentional interest signal from one user to another.
    """

    STATUS_CHOICES = ("sent", "accepted", "withered")

    sender_id = StringField(required=True)
    receiver_id = StringField(required=True)

    note = StringField(max_length=100, required=True)
    status =  StringField(choices=["sent", "accepted", "withered"], default="sent")

    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(default=lambda: datetime.utcnow() + timedelta(hours=24))
    accepted_at = DateTimeField()
    withered_at = DateTimeField()
    cooldown_until = DateTimeField(default=lambda: datetime.utcnow() + timedelta(hours=72))

    meta = {
        "collection": "flowers",
        "indexes": [
            {"fields": ["sender_id", "receiver_id"]},
            {"fields": ["status"]},
            {"fields": ["expires_at"]},
            {"fields": ["cooldown_until"]},
        ],
    }

    # --- Utility methods ---

    def mark_accepted(self):
        """Mark this flower as accepted and update timestamps."""
        self.status = "accepted"
        self.accepted_at = datetime.utcnow()
        self.save()

    def mark_withered(self):
        """Mark this flower as withered after expiry."""
        self.status = "withered"
        self.withered_at = datetime.utcnow()
        self.save()

    def is_expired(self):
        """Check if flower expired (for worker jobs)."""
        return self.status == "sent" and datetime.utcnow() > self.expires_at

    @classmethod
    def can_send(cls, sender_id: str, receiver_id: str):
        """
        Validate if sender can send a flower to receiver.
        - Must have <= 3 sent today.
        - Must not have sent to the same receiver in past 72h.
        """
        now = datetime.utcnow()

        sent_today = cls.objects(
            sender_id=sender_id,
            created_at__gte=now.replace(hour=0, minute=0, second=0, microsecond=0),
        ).count()

        recent_flower = cls.objects(
            sender_id=sender_id,
            receiver_id=receiver_id,
            created_at__gte=now - timedelta(seconds=7)
        ).first()

        if sent_today >= 3:
            return False, "Daily flower limit reached."
        if recent_flower:
            return False, "You can send again to this user after 72 hours."

        return True, None