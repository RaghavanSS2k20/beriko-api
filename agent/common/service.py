from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage
from .llm import llm

def generate_user_friendly_profile(persona_text: str) -> dict:
    """
    Converts raw behavioral and psychological persona text
    into a short, user-facing profile description.

    Returns:
        dict: {
            "success": bool,
            "data": str (if success),
            "error": str (if failed)
        }
    """
    try:
        prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        """You are an intelligent assistant that converts detailed behavioral and psychological data
        into a short, friendly, user-facing profile description (2–3 sentences).

        Persona Data:
        {persona_text}

        Guidelines:
        - Write in a **friendly, second-person style** (use "You", not "I" or "they").
        - Make it **personalized**, like the app is observing and noticing the user.
        - Only describe what is directly supported by the data. Do **not** infer or exaggerate traits.
        - Keep it warm, simple, and natural — like something someone would read on a dating or social profile.
        - Avoid analytical or formal words like "score", "tendencies", or "exhibits".
        - Do not use metaphors, poetic phrases, or generic filler.
        - Focus on personality, emotions, and general vibe clearly and factually.
        -Do not miss any values to include in the description or else you wil be heavily penalised!
        """
    )
        ])





        response = llm([HumanMessage(content=prompt.format(persona_text=persona_text))])
        profile_description = response.content
        return {"success": True, "data": profile_description}

    except Exception as e:
        print("LLM CALL FAILED ", e)
        return {"success": False, "error": str(e)}
