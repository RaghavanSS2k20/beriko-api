import asyncio
from .llm import llm
from agent.profilebuilder.service import handle_engine_call
from concurrent.futures import ThreadPoolExecutor

from  entities.user.user_service import get_chats


# global thread pool
executor = ThreadPoolExecutor(max_workers=5)


def format_history(chats: list) -> list:
    """
    Convert DB chat history into LLM-friendly format.
    """
    history = []
    for c in chats:
        if c["sender"] == "user":
            history.append({"role": "user", "content": c["content"]})
        elif c["sender"] == "agent":
            history.append({"role": "assistant", "content": c["content"]})
    return history

def generate_conversation_reply(content,user_id):
    print(content)
    chats = get_chats(user_id)
    
    history = format_history(chats["data"])
    print(history)
    messages = history + [{"role": "user", "content": content}]
    res = llm.invoke(messages)
    reply = res.content
    print("RES HERE : ",res.content)
    # asyncio.create_task(handle_engine_call(user_id, content))
    executor.submit(handle_engine_call, user_id, content)
    return reply
