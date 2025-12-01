from .prompt import prompt
from agent.profilebuilder.llm import llm, parser, prompt_template
import requests
from environment import ENGINE_URL
import time

def generate_weigths(content, history_weights):
    # return "Hiis"
    print("Generate weights called : ", content, history_weights)
    chain = prompt_template | llm | parser
    try:
        res = chain.invoke({"prompt_text": prompt(content, history_weights)})
        print("✅ RES HERE:", res)

        weights = res.json()  # assuming parser produces JSON
        if isinstance(weights, str):
            # try to convert string to dict
            import json
            weights = json.loads(weights)
        return weights
    except Exception as e:
        print("❌ ERROR:", e)


def handle_engine_call(user, content, history):
    start_time = time.time()
    print(f"[{start_time:.2f}] 🚀 Handle Engine call started | User: {user}")

    # 1️⃣ Build history text
    print(f"[{time.time():.2f}] 🧩 Building chat history")
    history_text = ""
    for chat in history[::-1]:
        sender_label = "You" if chat["role"] == "user" else "Agent"
        history_text += f"{sender_label}: {chat['content']}\n"
        print(f"[{time.time():.2f}] Added {sender_label} line")
    print(f"[{time.time():.2f}] ✅ HISTORY BUILT:\n{history_text}")

    # 2️⃣ Generate weights
    print(f"[{time.time():.2f}] ⚙️ Generating weights")
    weights = generate_weigths(content, history_text)
    print(f"[{time.time():.2f}] ✅ Weights generated: {weights} ({type(weights)})")

    # 3️⃣ Call Engine
    try:
        print(f"[{time.time():.2f}] 🌐 Calling Engine API: {ENGINE_URL}/trait/update")
        response = requests.put(
            f"{ENGINE_URL}/trait/update",
            json={"user_id": user, "weights": weights},
            timeout=5  # ⏰ add timeout here
        )
        print(f"[{time.time():.2f}] 🔁 Engine responded, checking status...")
        response.raise_for_status()

        print(f"[{time.time():.2f}] ✅ Engine call success | Elapsed: {time.time() - start_time:.2f}s")
        return {"success": True, "data": response.json()}

    except requests.RequestException as e:
        print(f"[{time.time():.2f}] ❌ Engine call failed: {e} | Elapsed: {time.time() - start_time:.2f}s")
        return {"success": False, "error": str(e)}

    finally:
        print(f"[{time.time():.2f}] 🏁 handle_engine_call finished | Total time: {time.time() - start_time:.2f}s") 
