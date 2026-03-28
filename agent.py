# ===== IMPORTS =====
import os
import time
import warnings

# Suppress Pydantic V1 compatibility warnings (Python 3.14+)
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality")

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# ===== LOAD ENV =====
load_dotenv()

# ===== SUPPORTED MODELS (in priority order) =====
# If one model's quota is exhausted, we fall back to the next
MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
]

# ===== LLM FACTORY =====
def get_llm(model: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set in .env file.")
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.1,
        max_retries=2,
    )

# ===== PROMPT BUILDER =====
def build_prompt(code: str, language: str) -> str:
    return f"""
You are 'DebugMind AI Pro'—an advanced AI debugging agent.

You are an expert compiler and static analyzer for multiple programming languages including:
Python, Java, C, C++, C#, HTML, CSS, JavaScript, TypeScript, Go, and Rust.

TASK: Analyze the following {language} code.
1. Detect ANY syntax errors, compilation errors, or logic bugs.
2. Explain what the error is clearly.
3. Provide the corrected version of the code.

ORIGINAL SOURCE:
```{language}
{code}
```

Please structure your final report precisely as follows:

### 🧠 AI Analysis Process
(Briefly explain your thought process as you scanned the code for syntax, logic, security, and performance issues.)

### 🚨 Detected Errors
(List the specific syntax errors and bugs found. If none, state that the code is functional but optimizations can be made.)

### 💡 Technical Explanation
(Provide a clear and simple explanation of the errors and how they affect the program.)

### 🛠️ Fixed Source Code
(Provide the fully corrected and working version in a single markdown code block.)

### 🚀 Best Practices & Optimization
(Suggest ways to improve the code architecturally or functionally.)
"""

# ===== FUNCTION TO RUN AGENT WITH FALLBACK =====
def run_agent(code: str, language: str) -> str:
    """
    Try each model in priority order.
    If a model hits a quota/rate-limit error (429), fall back to the next one.
    Retries once after a short wait on transient errors.
    """
    prompt = build_prompt(code, language)
    last_error = None

    for model in MODELS:
        for attempt in range(2):  # up to 2 attempts per model
            try:
                llm = get_llm(model)
                response = llm.invoke(prompt)
                return response.content

            except Exception as e:
                error_str = str(e)
                last_error = e

                is_quota = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
                is_rate   = "rate" in error_str.lower()

                if is_quota:
                    # This model's daily/minute quota is gone — try next model
                    print(f"[DebugMind] Model '{model}' quota exhausted. Trying next model...")
                    break  # break retry loop, go to next model

                elif is_rate and attempt == 0:
                    # Transient rate limit — wait & retry once
                    print(f"[DebugMind] Rate limit hit on '{model}'. Waiting 5s before retry...")
                    time.sleep(5)
                    continue

                else:
                    # Unknown error — surface it immediately
                    raise

    # All models exhausted
    raise last_error