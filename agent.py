# ===== IMPORTS =====
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
import os

# ===== LOAD ENV =====
load_dotenv()

# ===== DEFINE TOOLS =====

@tool
def syntax_checker(code: str) -> str:
    """Check for basic syntax errors like missing colons in Python."""
    if "for" in code and ":" not in code:
        return "Possible syntax error: Missing ':' in loop"
    return "No obvious syntax issues found"

@tool
def bug_detector(code: str) -> str:
    """Identify common logic bugs like using assignment = instead of comparison ==."""
    if "=" in code and "==" not in code:
        return "Possible bug: Assignment used instead of comparison"
    return "No major bugs detected"

# ===== LLM SETUP =====
def get_llm():
    return ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )

# ===== FUNCTION TO RUN AGENT =====
def run_agent(code, language):
    # Since initialize_agent is not available in this version, we'll use a clean tool-binding approach.
    llm = get_llm()
    tools = [syntax_checker, bug_detector]
    
    # We'll use a prompt-based approach to simulate the agent logic since the user wants to see tool usage.
    prompt = f"""
    You are a professional Debugging Assistant.
    Analyze this {language} code:
    
    {code}
    
    First, I have run these tools:
    - Syntax Checker: {syntax_checker.run(code)}
    - Bug Detector: {bug_detector.run(code)}
    
    Based on these results and your knowledge, provide a final response with:
    1. Errors:
    2. Explanation:
    3. Fixed Code:
    """
    
    response = llm.invoke(prompt)
    return response.content