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
                into a **short, friendly, user-facing profile description** that is easy to read.
                
                Persona Data:
                {persona_text}
                
                Write a crisp 2-3 sentence description as a user would see in a profile."""
            )
        ])

        response = llm([HumanMessage(content=prompt.format(persona_text=persona_text))])
        profile_description = response.content
        return {"success": True, "data": profile_description}

    except Exception as e:
        print("LLM CALL FAILED ", e)
        return {"success": False, "error": str(e)}
