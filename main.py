# ===== IMPORTS =====
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent import run_agent

# ===== LOAD ENV =====
load_dotenv()

# ===== INIT APP =====
app = FastAPI()

# ===== ENABLE CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== REQUEST MODEL =====
class CodeInput(BaseModel):
    code: str
    language: str

# ===== DEBUG ENDPOINT =====
@app.post("/debug")
async def debug_code(data: CodeInput):
    try:
        result = run_agent(data.code, data.language)
        return {"result": result}

    except Exception as e:
        error_msg = str(e)
        print("Error:", error_msg)

        if "429" in error_msg or "quota" in error_msg.lower():
            # Mock the Agent response when the API limit hits
            return {"result": f"""Action: syntax_checker
Action Input: "{data.code}"
Observation: No obvious syntax issues found
Thought: The code seems structurally okay, let me check for other logical bugs.
Action: bug_detector
Action Input: "{data.code}"
Observation: Possible bug: Assignment used instead of comparison or out-of-bounds loop
Thought: I need to correct this.

1. Errors:
- Loop bounds mismatch or missing variables.
- AI actual execution paused due to simulated testing API limits (`sk-proj-...`).

2. Explanation:
- The backend successfully relayed your request to the new Langchain AI Agent, however the OpenAI API key is exhausted. 
- You are viewing an intercepted Agent mock response!

3. Fixed Code:
```javascript
{data.code.replace('i--', 'i++')} // Simulated Fix via Agent Tool
```

4. Best Practices:
- Renew API Key in `.env` to make this Langchain Agent live!
"""}

        return {
            "result": f"""
AI Agent Error Occurred ❌

Reason:
{error_msg}

Tip:
- Check your API key.
- Check if agent.py is working.
- Restart server.
"""
        }

# ===== RUN SERVER =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)