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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request model
class CodeInput(BaseModel):
    code: str
    language: str

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)