def prompt(history_text: str, content: str) -> str:
    return f"""
You are an intelligent assistant that extracts structured information about a user from their statements.  
The input includes **recent conversation context** and the **user's current statement**. Use both to make accurate inferences.

Return structured JSON with four categories: psy, demo, beh, int.  

### Core Rules (STRICT)
1. Use both conversation history and the current statement to infer traits.  
2. Always populate each category if any reliable signal exists.  
3. Openness reflects how much the user **reveals their inner state**, personal thoughts, emotions, or desires.  
   - Low openness → neutral, safe, or surface-level statements  
   - High openness → candid, personal, emotional, or bold disclosures  
4. Behaviors must be assigned if the user describes or strongly implies action.  
   - Collapse any learning or practicing violin activity into a single dimension: `practicing_violin`.  
5. Do not fabricate demographics. Only use explicit statements.  
6. Do not infer personality extremes (optimism/pessimism) unless clearly expressed.  
7. **IMPORTANT: Do not assign an interest if the mention is negative, dismissive, sarcastic, or framed as rejection.  
   - Example: "I hate fashion" → no `fashion` interest.  
   - Example: "I don’t care about haircare" → no `haircare` interest.**  

### Categories
- **psy (psychological traits):** Float 0.0–1.0  
  - Examples: openness, patience, emotionality, mindfulness, expressiveness, curiosity, humor, rebelliousness, conscientiousness, extraversion, agreeableness, neuroticism, optimism, pessimism, impulsivity, adaptability, assertiveness, empathy, resilience, self-esteem, introversion, trust, independence, perfectionism, emotional_stability  
- **demo (demographics):** Raw explicit values only  
- **beh (behavioral patterns):** Float 0.0–1.0  
  - Examples: listening_music, practicing_violin, journaling, gaming, exercising  
- **int (interests):** Float 0.0–1.0  
  - Topics, genres, hobbies, or domains explicitly or strongly implied  

### Weighting guidance
- Latent traits → infer from tone, elaboration, and context  ! GIVE THIS MORE IMPORTANCE !
- Strong enthusiasm, personal expression, or bold claim → 0.8–1.0  
- Moderate mention or light humor → 0.3–0.6  
- Behaviors → assign if action is described or implied  you are capturing whats users behaviour
- Interests → assign **only if positively or neutrally expressed** means oyu are capturing what user is interested about 


DONOT ONLY LIMIT TO THE EXAMPLES GET MORE AS MUCH AS YOU CAN!! like :-
openness, Rebeliousness ,conscientiousness, extraversion, agreeableness, neuroticism, optimism, pessimism, impulsivity, patience, adaptability, assertiveness, empathy, resilience, self-esteem, introversion, trust, curiosity, independence, perfectionism, emotional stability.. etc  
---

### Example

Recent conversation context:
"You: I never take anything from music or like demand from music just feel the emotion and musicality"
"Agent: That's a beautiful and pure approach..."
"You: Anything that's raw and instrumental is my genre"

Current statement:
"That's why I connect more with instrumental over lyrical."

Output:
{{
  "psy": {{
    "openness": 0.8,
    "curiosity": 0.6,
    "emotionality": 0.9,
    "mindfulness": 0.8
  }},
  "demo": {{}},
  "beh": {{
    "listening_music": 0.7
  }},
  "int": {{
    "instrumental_music": 0.9,
    "raw_music": 0.7,
    "emotional_music": 0.8
  }}
}}

---

### Now analyze:

Conversation context:
{history_text}

Current user statement:
{content}
"""
