from .prompt import prompt
from agent.profilebuilder.llm import llm, parser, prompt_template
import requests
from environment import ENGINE_URL

def generate_weigths(content):
    # return "Hiis"
    print("Generate weights called")
    chain = prompt_template | llm | parser
    try:
        res = chain.invoke({"prompt_text": prompt(content)})
        print("✅ RES HERE:", res)
        return res.json()
    except Exception as e:
        print("❌ ERROR:", e)


def handle_engine_call(user, content):
    weights = generate_weigths(content)
    print(weights)
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
        response.raise_for_status()  # raises if not 2xx
        return {"success": True, "data": response.json()}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}