import os
import sys
import time
import json
import requests
import pyautogui
import keyboard
import pyperclip
from typing import Dict, TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Dynamically ensure top-level project module access
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import Phase 5 & Phase 6 custom engine modules
from src.ingestion.screen_capture import ScreenContextLayer
from src.ingestion.ocr_reader import GMAScreenOCRReader
from src.execution.action_bridge import SystemOperatorBridge

# Configure Safety Constraints for Desktop Automation
pyautogui.FAILSAFE = True  
pyautogui.PAUSE = 0.05     

# 1. Define the Structured State of the Human Mind Extension
class GMState(TypedDict):
    raw_user_input: str          
    captured_context: str        
    normalized_intent: Dict      
    proposed_actions: List[Dict] 
    approval_status: str         

# Initialize Local SQLite Ledger to preserve execution states during human pauses
import sqlite3
db_connection = sqlite3.connect("gm_memory.db", check_same_thread=False)
memory = SqliteSaver(db_connection)

# Instantiating our newly integrated modular sub-layers
screen_layer = ScreenContextLayer()
ocr_engine = GMAScreenOCRReader()
operator_bridge = SystemOperatorBridge()

# 2. Node: Capture Screen Context (The AI's Eyes - Now powered by OCR Scanning)
def capture_context_node(state: GMState) -> Dict:
    print("\n[GM AI] [Eyes Active] Snapshotting screen and running OCR character trace scanner...")
    
    # Grab the active display frame path matrix
    cached_frame_path = screen_layer.capture_full_display()
    
    # Run the raw frame path through your newly integrated OCR layer
    extracted_text = ocr_engine.extract_text_from_matrix(cached_frame_path)
    
    # If the screen text layout returns empty, fall back onto clipboard string arrays safely
    if not extracted_text.strip() or "SYSTEM_FALLBACK" in extracted_text:
        clipboard_text = pyperclip.paste().strip()
        extracted_text = f"[OCR Fallback/Clipboard] {clipboard_text if clipboard_text else 'General UI Canvas Focus'}"
        
    return {
        "captured_context": f"OCR Visual Text Map: '{extracted_text}' | Frame Anchor: {cached_frame_path}"
    }

# 3. Node: Parse Intent via Local Ollama (The AI's Brain)
def parse_intent_node(state: GMState) -> Dict:
    print("[GM AI] [Brain Active] Normalizing rough instructions via Ollama...")
    ollama_url = "http://localhost:11434/api/generate"
    
    system_prompt = (
        "You are GM AI, a seamless extension of the human mind. Convert the user's raw, "
        "fragmented instruction into a highly structured JSON automation plan containing an array of 'steps'. "
        "Each step must be an object with 'type' ('click_element', 'type_text', or 'press_key') and 'payload'.\n"
        "For 'click_element', the payload must match an application structural key (e.g., 'notepad.edit_field')."
    )
    
    prompt_payload = f"Sensed Screen OCR Layout: {state['captured_context']}\nUser Intent Input: {state['raw_user_input']}"
    
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
        user_lower = state['raw_user_input'].lower()
        if "click" in user_lower or "notepad" in user_lower:
            steps = [
                {"type": "click_element", "payload": "notepad.edit_field"},
                {"type": "type_text", "payload": "echo GM AI OCR Matrix Integrated!"}
            ]
        else:
            steps = [
                {"type": "type_text", "payload": "GM AI Automated Entry"},
                {"type": "press_key", "payload": "enter"}
            ]
        structured_steps = {"steps": steps}

    return {
        "normalized_intent": structured_steps, 
        "proposed_actions": structured_steps.get("steps", []), 
        "approval_status": "pending"
    }

# 4. Conditional Edge: The Core Safety Gatekeeper
def safety_gate_condition(state: GMState) -> str:
    if state.get("approval_status") == "approved":
        return "execute_macros"
    return END 

# 5. Node: Execute Automation via Peripheral Injection (The AI's Hands)
def execute_macros_node(state: GMState) -> Dict:
    print("\n[GM AI] [Hands Active] Executing user-approved spatial action sequence...")
    time.sleep(1.0) 
    
    for step in state["proposed_actions"]:
        action_type = step["type"]
        payload = step["payload"]
        
        if action_type == "click_element":
            if "." in payload:
                app_key, element_key = payload.split(".", 1)
                operator_bridge.execute_targeted_click(app_key, element_key)
            else:
                print(f"[GM AI Error] Invalid click target format: {payload}")
                
        elif action_type == "type_text":
            operator_bridge.execute_text_input(payload, press_enter=False)
            
        elif action_type == "press_key":
            pyautogui.press(payload)
            
    print("[GM AI] Action sequence completed successfully.")
    return {}

# 6. Assemble the Graph State Workflow Architecture
workflow = StateGraph(GMState)
workflow.add_node("capture_context", capture_context_node)
workflow.add_node("parse_intent", parse_intent_node)
workflow.add_node("execute_macros", execute_macros_node)

workflow.set_entry_point("capture_context")
workflow.add_edge("capture_context", "parse_intent")

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
    print("GM AI v1.6 — Integrated Multimodal OCR Engine Active")
    print("======================================================")
    
    user_input = input("Describe what you want to do in simple/broken English: ")
    print("\n[Action Required]: Leave your target application window open and active now.")
    time.sleep(2.0)
    
    initial_state = {"raw_user_input": user_input, "approval_status": "pending"}
    for event in gm_engine.stream(initial_state, thread_config):
        pass
        
    current_state = gm_engine.get_state(thread_config).values
    
    print("\n=========== 🛡️ GM AI BOT-SITTER SCREEN PREVIEW ===========")
    print(f"Captured OCR Context: {current_state['captured_context']}")
    print("\nProposed Automation Steps Blueprint:")
    for idx, step in enumerate(current_state['proposed_actions'], 1):
        print(f" [{idx}] Action Mode: {step['type']} -> Context: {step['payload']}")
    print("===========================================================")
    
    user_approval = input("\nDo you approve GM AI to execute this plan into your active app? (y/n): ")
    if user_approval.lower() == 'y':
        gm_engine.update_state(thread_config, {"approval_status": "approved"}, as_node="parse_intent")
        for event in gm_engine.stream(None, thread_config):
            pass
    else:
        print("[GM AI] Operation blocked by human operator. Environment pristine.")
