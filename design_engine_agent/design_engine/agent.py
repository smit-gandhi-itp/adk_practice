import asyncio
import uuid
from google.adk.agents import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.events import Event, EventActions
from litellm import close_litellm_async_clients
from datetime import datetime
import time
from .question_generation_agent import question_generation_agent
from .design_document_agent import  design_document_agent
from .utils import (
    ask_text,
    ask_single_choice,
    ask_multi_choice,
    run_phase_1_design_engine,
    run_phase_2_clarification_engine,
    render_phase3_design_to_word,
)


# =========================
# Agent / Session Configuration
# =========================

APP_NAME = "Agentic Design Engine"
USER_ID = "design_user"
SESSION_ID = str(uuid.uuid4())


# =========================
# Main Async Entry Point
# =========================

async def main():
    print("=== Initializing Agentic Design Engine ===")

    # -----------------
    # Initialize Root Agent (Phase 2 question generation)
    # -----------------
    root_agent = SequentialAgent(
        name="design_engine",
        sub_agents=[question_generation_agent],
        description=(
            "Pipeline: Phase 1 collects initial inputs, "
            "Phase 2 generates clarification questions."
        ),
    )
    print("✅ Initialized Root Sequential Agent for Phase 2.")

    # -----------------
    # Initialize Session Service
    # -----------------
    session_service_stateful = InMemorySessionService()
    print("✅ Initialized In-Memory Session Service.")

    # -----------------
    # Phase 1: Collect Initial Inputs
    # -----------------
    phase_1_inputs = run_phase_1_design_engine()

    initial_state = {"phase_1_inputs": phase_1_inputs}
    await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )
    print(f"✅ Session created: {SESSION_ID}")
    print("\n=== Phase 1 Inputs Collected ===")
    for k, v in phase_1_inputs.items():
        print(f"{k}: {v}")

    # -----------------
    # Phase 2: Generate Clarification Questions
    # -----------------
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    new_message = types.Content(
        role="user",
        parts=[types.Part(
            text="Based on Phase 1 inputs, generate clarification questions to finalize the system design."
        )]
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            print("\n=== Phase 2 Questions Generated ===")
            print(event.content.parts[0].text)

    # -----------------
    # Fetch Phase 2 Questions from Session
    # -----------------
    session = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    phase_2_clarification_questions = session.state.get("phase_2_clarification_questions", {})
    print("\n=== Phase 2 Questions Fetched from Session ===")
    for k in phase_2_clarification_questions.get("questions", {}).keys():
        print(f"- {k}")

    # -----------------
    # Phase 2: Collect User Answers
    # -----------------
    phase_2_answers = run_phase_2_clarification_engine(phase_2_clarification_questions)

    # Persist Phase 2 Answers into the same session (event-based)
    persist_event = Event(
        invocation_id=f"phase_2_answers_{int(time.time() * 1000)}",
        author="system",
        actions=EventActions(
            state_delta={
                "phase_2_answers": phase_2_answers,
                "phase_2_completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ),
        timestamp=time.time(),
    )
    await session_service_stateful.append_event(session, persist_event)
    print("✅ Phase 2 answers persisted in session.")

    # -----------------
    # Phase 3: Generate Full System Design Document
    # -----------------
    design_agent_runner = Runner(
        agent=SequentialAgent(
            name="design_engine_generation",
            sub_agents=[design_document_agent]
        ),
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    design_message = types.Content(
        role="user",
        parts=[types.Part(
            text="Using all available session context, generate the full system design document."
        )]
    )

    async for event in design_agent_runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=design_message,
    ):
        if event.is_final_response():
            print("\n=== Phase 3 System Design Document ===")
            print(event.content.parts[0].text)

    
    session = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    system_design_document = session.state.get("phase_3_system_design", {})
    print("\n=== Final System Design Document Fetched from Session ===")
    print(system_design_document)

    # -----------------
    # Render System Design Document to Word
    # -----------------
    output_word_path = "system_design_document.docx"
    render_phase3_design_to_word(system_design_document, output_word_path)
    print(f"✅ System design document rendered to Word: {output_word_path}")

    # -----------------
    # Cleanup
    # -----------------
    await close_litellm_async_clients()
    print("✅ Pipeline completed successfully.")


# ✅ Run
if __name__ == "__main__":
    asyncio.run(main())
