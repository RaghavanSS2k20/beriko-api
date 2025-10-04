from .prompt import prompt
from agent.profilebuilder.llm import llm, parser, prompt_template
import requests
from environment import ENGINE_URL

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
    print("Handle Engine call Called ", history)
    history_text = ""
    for chat in history[::-1]:
        sender_label = "You" if chat["role"] == "user" else "Agent"
        history_text += f"{sender_label}: {chat['content']}\n"
        print("CHATTTSTSTS")
    print("HISTORY HERE : ", history_text)
    weights = generate_weigths(content, history_text)
    print(weights, type(weights))
    try:
        # Example: calling your Engine API
        response = requests.put(
            f"{ENGINE_URL}/trait/update",   # change URL
            json={
                "user_id": user,
                "weights": weights
            },
            # timeout=5
        )
        print("✅ Engine call success")
        response.raise_for_status()  # raises if not 2xx
        return {"success": True, "data": response.json()}
    except requests.RequestException as e:
        print("❌ Engine called Failed : ", e)
        return {"success": False, "error": str(e)}