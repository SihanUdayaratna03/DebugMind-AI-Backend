# ===== IMPORTS =====
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# ===== LOAD ENV =====
load_dotenv()

# ===== LLM SETUP =====
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )

# ===== FUNCTION TO RUN AGENT =====
def run_agent(code, language):
    llm = get_llm()
    
    prompt = f"""
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
    
    response = llm.invoke(prompt)
    return response.content