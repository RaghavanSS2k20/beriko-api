import asyncio
from .llm import llm
from agent.profilebuilder.service import handle_engine_call
from concurrent.futures import ThreadPoolExecutor
from .prompt import addon_prompt
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

# def generate_conversation_reply(content, user_id):
#     print("User input:", content)
    
#     chats = get_chats(user_id)
    
#     if chats.get("success"):
#         history = format_history(chats["data"])
#         print(history)
#         sorted_chats = history[::-1]
#         last_pairs_chats = sorted_chats[:4]
#     else:
#         print(f"⚠ Error fetching chats for user {user_id}: {chats.get('error')}")
#         history = []
#         last_pairs_chats = []

#     print("Chat history:", history)
#     print("Last 2 pairs (for engine):", last_pairs_chats)
    
#     messages = history + [{"role": "user", "content": content}]
#     res = llm.invoke(messages)
#     reply = res.content
#     print("LLM reply:", reply)
    
#     executor.submit(handle_engine_call, user_id, content, last_pairs_chats)
#     print("hii")
#     return reply
def generate_conversation_reply(content, user_id):
    print("User input:", content)
    
    # Fetch chat history
    chats = get_chats(user_id)
    
    if chats.get("success"):
        history = format_history(chats["data"])
        print("Full chat history:", history)
        # Get last 4 pairs (for engine)
        sorted_chats = history[::-1]
        last_pairs_chats = sorted_chats[:4]
    else:
        print(f"⚠ Error fetching chats for user {user_id}: {chats.get('error')}")
        history = []
        last_pairs_chats = []

    print("Last 2 pairs (for engine):", last_pairs_chats)
    
    # Prepend Beriko identity prompt to the current user message
    prompt_with_identity = addon_prompt(content)
    
    # Combine history + current prompt
    messages = history + [{"role": "user", "content": prompt_with_identity}]
    
    # Invoke the LLM
    res = llm.invoke(messages)
    reply = res.content
    print("LLM reply:", reply)
    
    # Async: update profile / engine
    executor.submit(handle_engine_call, user_id, content, last_pairs_chats)
    
    return reply
