# 🍐 Beriko API Layer Documentation  

---

## 1. Introduction  

Beriko isn’t just a chatbot. It’s a **dual-agent system**:  
- One agent talks to you.  
- The other silently learns from you.  

This doc explains:  
1. What the two agents do.  
2. How data flows between them.  
3. Why we split synchronous vs. asynchronous work.  
4. How concurrency makes the whole thing feel like magic (instant yet evolving).  

---

## 2. The Two Agents  

### A. Conversational Agent  
- **Name:** `ConversationalAgent`  
- **Job:** Give the user a reply *now*.  
- **How it works:**  
  - Takes the incoming message.  
  - Calls the LLM (Gemini) synchronously.  
  - Returns text immediately.  
- **Why sync:** If users wait even 3 seconds, it feels broken. Chat must be real-time.  

---

### B. Profile Builder Agent  
- **Name:** `ProfileBuilderAgent`  
- **Job:** Enrich the user’s **digital twin profile** and refresh matches.  
- **How it works:**  
  - Runs in the background.  
  - Uses the same message the user sent, but instead of replying, it extracts **signals**.  
  - Traits are updated with normalized weights:  
    - **Psy (psychological)** → 0.0–1.0  
    - **Beh (behavioral)** → 0.0–1.0  
    - **Int (interests)** → 0.0–1.0  
    - **Demo (demographics)** → raw (age, city, gender…)  
  - Calls the **Engine Layer** to recompute matches.  
  - Stores results in DB for quick access.  

- **Why async:** Profiling and matching can take 1–2 seconds (LLM + compute). If we blocked chat on this, the user would sit staring at a spinner. Nobody likes that.  

---

## 3. Why Concurrency? (The Story)  

Imagine you’re chatting with Beriko:  

1. **You:** "I love hiking in the mountains!"  
2. **Conversational Agent** jumps in:  
   - "That sounds amazing! Do you usually go on solo hikes or with friends?"  
   - Reply speed: < 500ms → smooth.  
3. **Meanwhile…** Profile Builder Agent hears the same message, but instead of replying, it thinks:  
   - Hiking → interest: `outdoors = 0.9`  
   - Behavioral → `fitness_routine = 0.7`  
   - Psy → openness ticked up by 0.05  
   - Updates DB and asks the Engine: “Who else in the system is into outdoors?”  
   - Stores fresh matches in the DB.  
4. By the time you hit **/matches**, the DB already knows your hiking soulmate candidates.  

Without concurrency:  
- You’d wait 2–3 seconds for every message.  
- Reply + profiling + engine would pile up.  
- The chat experience would die.  

So concurrency is not a luxury — it’s survival.  
- **Sync path = front stage (talk).**  
- **Async path = backstage (learn + match).**  
- Together → seamless experience.  

---

## 4. Data Flow  
<img width="8293" height="2171" alt="Beriko-pipeline" src="https://github.com/user-attachments/assets/3981e959-2a4e-4fad-9e07-86240f2ffe2e" />

## 5. Engine Layer  

- **Job:** The “matchmaker brain.”  
- **Input:** Profile JSON.  
- **Process:**  
  - Psy + Beh → cosine similarity.  
  - Interests → Manhattan distance (normalized).  
  - Demographics → filters (hard gates like city, gender, age range).  
- **Output:** Ranked matches:  
```json
[
  { "user_id": "u123", "score": 0.92 },
  { "user_id": "u456", "score": 0.87 }
]
```

## Summary
The Beriko API layer orchestrates a seamless user experience by splitting responsibilities between two agents: the Conversational Agent, which handles incoming messages synchronously to provide instant LLM-generated replies, and the Profile Builder Agent, which asynchronously analyzes the same messages in the background to update user profiles and trigger the Engine for match computation. All computed matches are stored in the database, ensuring that API endpoints can retrieve results instantly without blocking the chat, allowing real-time conversations while continuously enriching profiles and maintaining up-to-date matchmaking.

`<>Coded with selfdoubt by Raghavan!</>`
Happy Self sabotaging!
