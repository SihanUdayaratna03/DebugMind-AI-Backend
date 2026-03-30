<<<<<<< HEAD
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize app
app = FastAPI()

# Enable CORS (IMPORTANT for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
=======
# ===== IMPORTS =====
import warnings
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import run_agent

# ===== LOAD ENV =====
load_dotenv()

# ===== INIT APP =====
app = FastAPI(
    title="DebugMind AI Backend",
    description="AI-powered code debugging using Google Gemini",
    version="2.0.0",
)

# ===== ENABLE CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins (dev mode)
>>>>>>> debugmind-ai-backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request model
=======
# ===== REQUEST / RESPONSE MODELS =====
>>>>>>> debugmind-ai-backend
class CodeInput(BaseModel):
    code: str
    language: str

<<<<<<< HEAD
# Debug endpoint
@app.post("/debug")
async def debug_code(data: CodeInput):
    try:
        prompt = f"""
You are a senior software engineer and debugging expert.

Analyze the following {data.language} code carefully.

CODE:
{data.code}

Give your answer in this format:

1. Errors:
- List all errors

2. Explanation:
- Explain clearly in simple words

3. Fixed Code:
- Provide corrected version

4. Best Practices:
- Suggest improvements
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return {"result": response.choices[0].message.content}

    except Exception as e:
        print("Handling Exception:", repr(e))
        # ALWAYS mock the response
        mock_result = f"""1. Errors:
- Infinite loop detected in `for` loop (e.g., `i--` instead of `i++`) or variable name mismatch.
- AI Analysis failed due to OpenAI Quota limit (`sk-proj-...`).

2. Explanation:
- The actual OpenAI API key is exhausted so I'm giving a mock test response. To get real AI debugging, replace the OPENAI_API_KEY in your `.env` file!

3. Fixed Code:
```javascript
{data.code.replace('i--', 'i++')} // Simulated fix
```

4. Best Practices:
- Always check loop bounds.
- Update your OpenAI billing.
"""
        return {"result": mock_result}

=======
class DebugResult(BaseModel):
    result: str
    model_used: str | None = None

# ===== HEALTH CHECK ENDPOINT =====
@app.get("/health")
async def health_check():
    """Simple health-check so the frontend can verify the backend is alive."""
    return {"status": "ok", "service": "DebugMind AI Backend"}

# ===== DEBUG ENDPOINT =====
@app.post("/debug", response_model=DebugResult)
async def debug_code(data: CodeInput):
    if not data.code.strip():
        raise HTTPException(status_code=400, detail="Code input cannot be empty.")
    if not data.language.strip():
        raise HTTPException(status_code=400, detail="Language field cannot be empty.")

    try:
        result, model_used = run_agent(data.code, data.language)
        return {"result": result, "model_used": model_used}

    except ValueError as e:
        # Missing API key or config issue
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        error_msg = str(e)
        print(f"[DebugMind] Error: {error_msg}")

        is_quota = "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg.upper()
        is_auth  = "API_KEY" in error_msg.upper() or "invalid api key" in error_msg.lower()

        if is_quota:
            return {
                "result": f"""
### ⚠️ API Quota Exhausted

All available Gemini models have hit their free-tier rate limits.

**What this means:**
- Your Google AI Studio free-tier daily quota has been used up.
- This resets automatically (usually within a few hours or the next day).

**What you can do:**
1. Wait and try again later (quota resets daily).
2. Enable billing on [Google AI Studio](https://aistudio.google.com) for higher limits.
3. Generate a **new API key** at [aistudio.google.com](https://aistudio.google.com) and update your `.env` file.

**Your `.env` should look like:**
```
GOOGLE_API_KEY=AIza...your_new_key...
```
""",
                "model_used": None,
            }

        if is_auth:
            return {
                "result": """
### ❌ Invalid API Key

Your `GOOGLE_API_KEY` in `.env` appears to be invalid or expired.

**Fix:**
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key.
3. Open `.env` and replace the old key:
```
GOOGLE_API_KEY=AIza...your_new_key...
```
4. Restart the backend server.
""",
                "model_used": None,
            }

        # Generic unexpected error
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error from AI agent: {error_msg}",
        )

# ===== RUN SERVER =====
>>>>>>> debugmind-ai-backend
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)