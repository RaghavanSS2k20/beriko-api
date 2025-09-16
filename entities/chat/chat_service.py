from .chat_model import Chat
from utils.response import send_response

def create_chat(sender: str, message: str):
    """Factory function to create a Chat object"""
    print("✅ Chat called")
    try:
        chat = Chat(
            sender=sender,
            content=message,
            # timestamp=datetime.utcnow()
        )
        # chat.save()   # 💾 writes to MongoDB
        print("✅ Chat saved:", chat)
        return chat
       
    except Exception as e:
        # Normally you'd raise here, but if you want uniform return:
        print("error : ",e)
        return None
