import os
import sys
import time
import json
import requests
import pyautogui
import keyboard
import pyperclip
from typing import Dict, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Configure Safety Constraints for Desktop Automation
pyautogui.FAILSAFE = True  # Slamming the mouse into the very top-left corner aborts the macro instantly
pyautogui.PAUSE = 0.05     # Crucial 50ms pause between actions to mimic rapid human typing safely

# 1. Define the Structured State of the Human Mind Extension
class GMState(TypedDict):
    raw_user_input: str          # The broken English spoken/typed command
    captured_context: str        # The raw text data scraped from the active screen
    normalized_intent: Dict      # Structured JSON plan parsed by the LLM
    proposed_actions: list       # Exact step-by-step array of keystrokes/clicks
    approval_status: str         # "pending", "approved", or "rejected"

# Initialize Local SQLite Ledger to preserve execution states during human pauses
import sqlite3
db_connection = sqlite3.connect("gm_memory.db", check_same_thread=False)
memory = SqliteSaver(db_connection)

# 2. Node: Capture Screen Context (The AI's Eyes)
def capture_context_node(state: GMState) -> Dict:
    print("\n[GM AI] [Eyes Active] Reading highlighted data from active screen context...")
    
    # We read whatever text is currently inside the clipboard buffer
    captured = pyperclip.paste()
    
    if not captured.strip():
        captured = "Blank window focus / Operating on general active application view."
        
    return {"captured_context": captured}

# 3. Node: Parse Intent via Local Ollama (The AI's Brain)
def parse_intent_node(state: GMState) -> Dict:
    print("[GM AI] [Brain Active] Normalizing rough instructions via Ollama...")
    ollama_url = "http://localhost:11434/api/generate"
    
    system_prompt = (
        "You are GM AI, a seamless extension of the human mind. Convert the user's raw, "
        "fragmented instruction and active screen context into a highly structured JSON "
        "automation plan containing an array of 'steps'. Each step must be an object with "
        "'type' ('type_text' or 'press_key') and 'payload'."
    )
    
    prompt_payload = f"Sensed Screen Context: {state['captured_context']}\nUser Intent Input: {state['raw_user_input']}"
    
    payload = {
        "model": "llama3",
        "prompt": f"{system_prompt}\n\n{prompt_payload}",
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(ollama_url, json=payload).json()
        structured_steps = json.loads(response['response'])
    except Exception:
        # Secure structural fallback data loop if Ollama is not initialized yet
        structured_steps = {"steps": [
            {"type": "type_text", "payload": "GM AI Automated Entry"},
            {"type": "press_key", "payload": "enter"}
        ]}

    return {
        "normalized_intent": structured_steps, 
        "proposed_actions": structured_steps.get("steps", []), 
        "approval_status": "pending"
    }

# 4. Conditional Edge: The Core Safety Gatekeeper
def safety_gate_condition(state: GMState) -> str:
    if state.get("approval_status") == "approved":
        return "execute_macros"
    # LangGraph structural freeze point. Holds state thread in database until un-halted
    return END 

# 5. Node: Execute Automation via Peripheral Injection (The AI's Hands)
def execute_macros_node(state: GMState) -> Dict:
    print("\n[GM AI] [Hands Active] Executing user-approved keystroke sequence...")
    time.sleep(1.0) # Grace period for the human to release physical keys
    
    for step in state["proposed_actions"]:
        if step["type"] == "type_text":
            pyautogui.write(step["payload"], interval=0.01)
        elif step["type"] == "press_key":
            pyautogui.press(step["payload"])
            
    print("[GM AI] Macro loop finished successfully. Returning to standby.")
    return {}

# 6. Assemble the Graph State Workflow Architecture
workflow = StateGraph(GMState)
workflow.add_node("capture_context", capture_context_node)
workflow.add_node("parse_intent", parse_intent_node)
workflow.add_node("execute_macros", execute_macros_node)

workflow.set_entry_point("capture_context")
workflow.add_edge("capture_context", "parse_intent")

# Wire the Bot-Sitter Intercept Boundary
workflow.add_conditional_edges(
    "parse_intent",
    safety_gate_condition,
    {"execute_macros": "execute_macros", END: END}
)
workflow.add_edge("execute_macros", END)
gm_engine = workflow.compile(checkpointer=memory)

# 7. Local Prototype Execution Shell Interface
if __name__ == "__main__":
    thread_config = {"configurable": {"thread_id": "global_session"}}
    print("======================================================")
    print("GM AI v1.0 — Universal Local State Engine Active")
    print("======================================================")
    
    user_input = input("Describe what you want to do in simple/broken English: ")
    print("\n[Action Required]: Highlight targeted raw text in your open app window now.")
    time.sleep(2.0)
    
    # Phase 1 Run: Sense context, parse steps, and trigger the safety freeze
    initial_state = {"raw_user_input": user_input, "approval_status": "pending"}
    for event in gm_engine.stream(initial_state, thread_config):
        pass
        
    current_state = gm_engine.get_state(thread_config).values
    
    # The "Co-Pilot Seat" Split-Screen Preview Window Terminal Representation
    print("\n=========== 🛡️ GM AI BOT-SITTER SCREEN PREVIEW ===========")
    print(f"Captured Text Context: '{current_state['captured_context']}'")
    print("\nProposed Automation Steps Blueprint:")
    for idx, step in enumerate(current_state['proposed_actions'], 1):
        print(f" [{idx}] Action Mode: {step['type']} -> Context: {step['payload']}")
    print("===========================================================")
    
    user_approval = input("\nDo you approve GM AI to execute this plan into your active app? (y/n): ")
    if user_approval.lower() == 'y':
        # Safely unfreeze database state and pass execution token downstream
        gm_engine.update_state(thread_config, {"approval_status": "approved"}, as_node="parse_intent")
        for event in gm_engine.stream(None, thread_config):
            pass
    else:
        print("[GM AI] Operation blocked by human operator. Environment pristine.")
