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
4. Behaviors must be assigned if the user describes or strongly implies action. How they respond in real world not in texts  
   - Collapse any learning or practicing violin activity into a single dimension: `practicing_violin`.  
5. Do not fabricate demographics. Only use explicit statements.  
6. Do not infer personality extremes (optimism/pessimism) unless clearly expressed.  
7. **Do not assign an interest if the mention is negative, dismissive, sarcastic, or framed as rejection.**  
   - Example: "I hate fashion" → no `fashion` interest.  
   - Example: "I don't care about haircare" → no `haircare` interest.  
8. **Do not assign an interest if the mention is part of a metaphor, comparison, or exaggeration.**  
   - Example: "my love for trains is near to ocean" → only `train` counts, not `ocean`.  
9. **Do not assign interests from generic platform or system-related phrases.**  
   - Example: "find matches", "open app", "login", "use AI" → these are functional, not interests.  
10. **If multiple nouns appear, prefer the emotionally owned one.**  
   - Example: "I love trains near the ocean" → `train` yes, `ocean` no.  
11. **Only extract actual personality traits, NOT verbs, verb forms, or linguistic artifacts.**
   - Extract the **underlying trait** that the language signals, not the literal words used
   - If a verb appears (wonder, think, feel, know, believe, want, hope), identify what personality trait it reveals
   - Trait names must represent stable psychological characteristics, not transient actions or grammatical constructs

### Categories
- **psy (psychological traits):** Float 0.0–1.0  
  - Must be stable personality characteristics, not verbs or actions
  - Examples: openness, patience, emotionality, mindfulness, expressiveness, curiosity, humor, rebelliousness, conscientiousness, extraversion, agreeableness, neuroticism, optimism, pessimism, impulsivity, adaptability, assertiveness, empathy, resilience, self_esteem, introversion, trust, independence, perfectionism, emotional_stability, thoughtfulness, introspection, sensitivity, playfulness, ambition, discipline, confidence
- **demo (demographics):** Raw explicit values only  
  - Examples: age, location, occupation, education, relationship_status, gender, ethnicity
- **beh (behavioral patterns):** Float 0.0–1.0  
  - Examples: listening_music, practicing_violin, journaling, gaming, exercising, train_gazing, reading, cooking, traveling, socializing, meditating, creating_art
- **int (interests):** Float 0.0–1.0  
  - Topics, genres, hobbies, or domains explicitly or strongly implied  
  - Examples: trains, music, photography, philosophy, science, sports, fashion, technology

### Weighting guidance
- Latent traits → infer from tone, elaboration, and context  **! GIVE THIS MORE IMPORTANCE !**  
- Strong enthusiasm, personal expression, or bold claim → 0.8–1.0  
- Moderate mention or light humor → 0.3–0.6  
- Behaviors → assign if action is described or implied  
- Interests → assign **only if positively or neutrally expressed**, and only if the topic shows genuine affection, curiosity, or ongoing engagement (not incidental mention).  

### Trait Inference Logic
When extracting psychological traits:
- Ask: "What does this language reveal about their **stable personality**?"
- Extract the **trait being signaled**, not the word being used
- Convert observations and actions into their underlying psychological meaning
- Focus on enduring characteristics, not momentary states or grammatical constructs

---

### Example 1

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

### Example 2

Conversation context:
(empty)

Current user statement:
"I love train gazing i always wonder why i love trains this much!!"

Output:
{{
  "psy": {{
    "openness": 0.9,
    "curiosity": 0.9,
    "emotionality": 0.8,
    "expressiveness": 0.8,
    "introspection": 0.7
  }},
  "demo": {{}},
  "beh": {{
    "train_gazing": 0.9
  }},
  "int": {{
    "trains": 0.9
  }}
}}

Note: Extract traits being **signaled** by the language, not the literal words. "Wonder" as a verb signals **curiosity** and **introspection**.

---

### Now analyze:

Conversation context:
{history_text}

Current user statement:
{content}
"""