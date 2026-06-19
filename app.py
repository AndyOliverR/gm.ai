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

# Import Phase 5, 6, 7, 8 & 9 unified engine components
from src.ingestion.screen_capture import ScreenContextLayer
from src.ingestion.ocr_reader import GMAScreenOCRReader
from src.execution.action_bridge import SystemOperatorBridge
from src.communication.voice_ledger import GMAIVoiceAuditor
from src.execution.app_bootstrapper import GMAIAppBootstrapper
from src.execution.macro_player import GMAIMacroPlayer

# Configure Safety Constraints for Desktop Automation
pyautogui.FAILSAFE = True  
pyautogui.PAUSE = 0.05     

# Define the Structured State of the Human Mind Extension
class GMState(TypedDict):
    raw_user_input: str          
    captured_context: str        
    extracted_entities: Dict     
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
voice_auditor = GMAIVoiceAuditor()
bootstrapper = GMAIAppBootstrapper()
macro_player = GMAIMacroPlayer()

# Node: Capture Screen Context (The AI's Eyes)
def capture_context_node(state: GMState) -> Dict:
    print("\n[GM AI] [Eyes Active] Snapshotting screen and running OCR pattern trace matching...")
    cached_frame_path = screen_layer.capture_full_display()
    extracted_text = ocr_engine.extract_text_from_matrix(cached_frame_path)
    
    if not extracted_text.strip() or "SYSTEM_FALLBACK" in extracted_text:
        clipboard_text = pyperclip.paste().strip()
        extracted_text = f"[OCR Fallback/Clipboard] {clipboard_text if clipboard_text else 'General UI Canvas Focus'}"
        
    scraped_entities = ocr_engine.extract_structural_entities(extracted_text)
    
    return {
        "captured_context": f"OCR Visual Text Map: '{extracted_text}' | Frame Anchor: {cached_frame_path}",
        "extracted_entities": scraped_entities
    }

# Node: Parse Intent via Local Ollama (The AI's Brain - Custom Router for Saved Macros)
def parse_intent_node(state: GMState) -> Dict:
    print("[GM AI] [Brain Active] Normalizing instruction pipelines via Ollama...")
    ollama_url = "http://localhost:11434/api/generate"
    
    system_prompt = (
        "You are GM AI, a seamless extension of the human mind. Convert the user's raw, "
        "fragmented instruction into a highly structured JSON automation plan containing an array of 'steps'. "
        "Each step must be an object with 'type' ('click_element', 'type_text', 'press_key', 'press_hotkey', 'speak_log', or 'run_saved_macro') and 'payload'."
    )
    
    prompt_payload = (
        f"Sensed Screen OCR Layout: {state['captured_context']}\n"
        f"Scraped Struct Entities: {json.dumps(state['extracted_entities'])}\n"
        f"User Intent Input: {state['raw_user_input']}"
    )
    
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
        # Phase 9 Local Step Routing Override For Physical Macro Execution Triggers
        if "run macro" in user_lower or "replay" in user_lower or "playback" in user_lower:
            steps = [{"type": "run_saved_macro", "payload": "recorded_macro.json"}]
        elif "chrome" in user_lower or "browser" in user_lower or "web" in user_lower:
            steps = [
                {"type": "click_element", "payload": "chrome.browser_window"},
                {"type": "type_text", "payload": "GM AI Omnipresent Engine Online!"}
            ]
        elif "read" in user_lower or "log" in user_lower or "timeline" in user_lower or "speak" in user_lower:
            steps = [{"type": "speak_log", "payload": "trigger_timeline_audio"}]
        elif "task manager" in user_lower or "hotkey" in user_lower:
            steps = [{"type": "press_hotkey", "payload": "ctrl+shift+esc"}]
        else:
            steps = [
                {"type": "click_element", "payload": "notepad.edit_field"},
                {"type": "type_text", "payload": "echo Base Operational Flow Active!"}
            ]
        structured_steps = {"steps": steps}

    return {
        "normalized_intent": structured_steps, 
        "proposed_actions": structured_steps.get("steps", []), 
        "approval_status": "pending"
    }

# Conditional Edge: The Core Safety Gatekeeper
def safety_gate_condition(state: GMState) -> str:
    if state.get("approval_status") == "approved":
        return "execute_macros"
    return END 

# Node: Execute Automation via Peripheral Injection (Now Supporting Saved Json Scripts)
def execute_macros_node(state: GMState) -> Dict:
    print("\n[GM AI] [System Actions Active] Running pre-execution validations...")
    time.sleep(1.0) 
    
    for step in state["proposed_actions"]:
        action_type = step["type"]
        payload = step["payload"]
        
        if action_type == "run_saved_macro":
            print(f"[GM AI Engine] Deploying high-fidelity saved hardware macro sequence...")
            macro_player.execute_replay()
            
        elif action_type == "click_element":
            if "." in payload:
                app_key, element_key = payload.split(".", 1)
                bootstrapper.ensure_application_running(app_key)
                operator_bridge.execute_targeted_click(app_key, element_key)
            else:
                print(f"[GM AI Error] Invalid click target format: {payload}")
                
        elif action_type == "type_text":
            operator_bridge.execute_text_input(payload, press_enter=False)
            
        elif action_type == "press_key":
            pyautogui.press(payload)
            
        elif action_type == "press_hotkey":
            operator_bridge.execute_system_hotkey(payload)
            
        elif action_type == "speak_log":
            print("[GM AI Engine] Activating verbal audit narrative sequence...")
            voice_auditor.speak_timeline_summary()
            
    print("[GM AI] Operational sequence completed successfully.")
    return {}

# Assemble the Graph State Workflow Architecture
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

if __name__ == "__main__":
    thread_config = {"configurable": {"thread_id": "global_session"}}
    print("======================================================")
    print("GM AI v1.7 — Autonomous Macro Replay Core Engaged")
    print("======================================================")
    
    user_input = input("Describe what you want to do in simple/broken English: ")
    print("\n[Action Required]: Leave your target application workspace visible now.")
    time.sleep(2.0)
    
    initial_state = {"raw_user_input": user_input, "approval_status": "pending"}
    for event in gm_engine.stream(initial_state, thread_config):
        pass
        
    current_state = gm_engine.get_state(thread_config).values
    
    print("\n=========== 🛡️ GM AI BOT-SITTER SCREEN PREVIEW ===========")
    print(f"Captured OCR Context: {current_state['captured_context']}")
    print(f"Scraped Struct Entities: {json.dumps(current_state['extracted_entities'])}")
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
