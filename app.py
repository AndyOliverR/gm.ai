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

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import Phase 5 through Phase 10 unified modular components
from src.ingestion.screen_capture import ScreenContextLayer
from src.ingestion.ocr_reader import GMAScreenOCRReader
from src.execution.action_bridge import SystemOperatorBridge
from src.communication.voice_ledger import GMAIVoiceAuditor
from src.execution.app_bootstrapper import GMAIAppBootstrapper
from src.execution.macro_player import GMAIMacroPlayer
from src.ingestion.layout_profiler import GMAILayoutProfiler
from src.execution.data_extractor import GMAIDataExtractor

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

import sqlite3
db_connection = sqlite3.connect("gm_memory.db", check_same_thread=False)
memory = SqliteSaver(db_connection)

screen_layer = ScreenContextLayer()
ocr_engine = GMAScreenOCRReader()
operator_bridge = SystemOperatorBridge()
voice_auditor = GMAIVoiceAuditor()
bootstrapper = GMAIAppBootstrapper()
macro_player = GMAIMacroPlayer()
profiler = GMAILayoutProfiler()
data_extractor = GMAIDataExtractor()

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

def parse_intent_node(state: GMState) -> Dict:
    print("[GM AI] [Brain Active] Normalizing instruction pipelines via Ollama...")
    ollama_url = "http://localhost:11434/api/generate"
    
    system_prompt = (
        "You are GM AI, a seamless extension of the human mind. Convert the user's raw, "
        "fragmented instruction into a highly structured JSON automation plan containing an array of 'steps'. "
        "Each step must be an object with 'type' ('click_element', 'type_text', 'press_key', 'press_hotkey', 'speak_log', 'run_saved_macro', or 'extract_intel') and 'payload'."
    )
    
    prompt_payload = (
        f"Sensed Screen OCR Layout: {state['captured_context']}\n"
        f"Scraped Struct Entities: {json.dumps(state['extracted_entities'])}\n"
        f"User Intent Input: {state['raw_user_input']}"
    )
    
    try:
        payload = {
            "model": "llama3",
            "prompt": f"{system_prompt}\n\n{prompt_payload}",
            "stream": False,
            "format": "json"
        }
        response = requests.post(ollama_url, json=payload).json()
        structured_steps = json.loads(response['response'])
    except Exception:
        user_lower = state['raw_user_input'].lower()
        
        # New Structural Routing Step Logic for Data Extraction Requests
        if "save" in user_lower or "extract" in user_lower or "log data" in user_lower or "dump" in user_lower:
            steps = [{"type": "extract_intel", "payload": "commit_active_variables"}]
        elif "profile" in user_lower or "scan window" in user_lower or "map" in user_lower:
            steps = [
                {"type": "click_element", "payload": "custom_target_app.center_focus"},
                {"type": "type_text", "payload": "echo Adaptive Profiler Configured!"}
            ]
        elif "go to" in user_lower or "visit" in user_lower or "http" in user_lower or ".com" in user_lower:
            target_url = "google.com"
            for entity_url in state['extracted_entities'].get("urls", []):
                target_url = entity_url
            steps = [
                {"type": "click_element", "payload": "chrome.url_bar"},
                {"type": "type_text", "payload": target_url},
                {"type": "press_key", "payload": "enter"}
            ]
        elif "run macro" in user_lower or "replay" in user_lower or "playback" in user_lower:
            steps = [{"type": "run_saved_macro", "payload": "recorded_macro.json"}]
        else:
            steps = [
                {"type": "click_element", "payload": "notepad.edit_field"},
                {"type": "type_text", "payload": "echo Base Pipeline Operational Sequence Complete!"}
            ]
        structured_steps = {"steps": steps}

    return {
        "normalized_intent": structured_steps, 
        "proposed_actions": structured_steps.get("steps", []), 
        "approval_status": "pending"
    }

def safety_gate_condition(state: GMState) -> str:
    if state.get("approval_status") == "approved":
        return "execute_macros"
    return END 

def execute_macros_node(state: GMState) -> Dict:
    print("\n[GM AI] [System Actions Active] Running pre-execution validations...")
    time.sleep(1.0) 
    
    for step in state["proposed_actions"]:
        action_type = step["type"]
        payload = step["payload"]
        
        if action_type == "extract_intel":
            # Fire our newly integrated data extraction module
            print(f"[GM AI Engine] Parsing extracted entities out of state tree graph...")
            result = data_extractor.export_scraped_entities(state["extracted_entities"])
            print(f"[GM AI Engine] Data extraction journal result marker: {result}")
            
        elif action_type == "run_saved_macro":
            macro_player.execute_replay()
            
        elif action_type == "click_element":
            if "." in payload:
                app_key, element_key = payload.split(".", 1)
                
                if app_key not in operator_bridge.layouts:
                    print(f"[GM AI Core] Application context '{app_key}' missing from configs. Initializing live element mapper...")
                    profiler.profile_active_window(app_key)
                    operator_bridge.layouts = operator_bridge._load_layouts()
                
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
            voice_auditor.speak_timeline_summary()
            
    print("[GM AI] Operational sequence completed successfully.")
    return {}

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
    print("GM AI v1.7 — Autonomous Data Extraction Core Engaged")
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
