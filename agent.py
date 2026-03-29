# ===== IMPORTS =====
import os
import sys
import time
import warnings

# Force UTF-8 stdout to avoid charmap errors on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Suppress Pydantic V1 compatibility warnings
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality")

from google import genai
from dotenv import load_dotenv

# ===== LOAD ENV =====
load_dotenv()

# ===== SUPPORTED MODELS (in priority order) =====
# These are confirmed available models from the google-genai SDK
MODELS = [
    "gemini-2.5-flash",       # Latest & most capable, try first
    "gemini-2.0-flash",       # Fast, reliable fallback
    "gemini-2.0-flash-lite",  # Lightweight fallback
]

# ===== CLIENT FACTORY =====
def get_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set in .env file.")
    return genai.Client(api_key=api_key)

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
def run_agent(code: str, language: str) -> tuple:
    """
    Try each model in priority order using google-genai SDK.
    If a model hits a quota/rate-limit error (429), fall back to the next one.
    Retries once after a short wait on transient errors.
    Returns a tuple: (response_content: str, model_used: str)
    """
    prompt = build_prompt(code, language)
    client = get_client()
    last_error = None

    for model in MODELS:
        for attempt in range(2):  # up to 2 attempts per model
            try:
                print(f"[DebugMind] Trying model: {model} (attempt {attempt + 1})")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                print(f"[DebugMind] [OK] Success with model: {model}")
                return response.text, model

            except Exception as e:
                error_str = str(e)
                last_error = e

                is_quota = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str.upper()
                is_rate   = "rate" in error_str.lower()
                is_auth   = "API_KEY" in error_str.upper() or "invalid api key" in error_str.lower()

                if is_auth:
                    # Bad API key — no point retrying other models
                    print(f"[DebugMind] Auth error: {error_str}")
                    raise

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
                    print(f"[DebugMind] Unexpected error on model '{model}': {error_str}")
                    raise

    # All models exhausted
    if isinstance(last_error, BaseException):
        raise last_error
    raise RuntimeError("All Gemini models are unavailable. Please try again later.")