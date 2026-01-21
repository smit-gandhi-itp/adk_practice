import asyncio
import uuid
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from question_answer_agent import question_answer_agent
from google.genai import types
from litellm import close_litellm_async_clients

async def main():
    session_service_stateful = InMemorySessionService()
    print("Initialized In-Memory Session Service for stateful sessions.")

    initial_state = {
        "user_name": "Brandon Hancock",
        "user_preferences": """
            I like to play Pickleball, Disc Golf, and Tennis.
            My favorite food is Mexican.
            My favorite TV show is Game of Thrones.
            Loves it when people like and subscribe to his YouTube channel.
        """,
    }

    APP_NAME = "Brandon Bot"
    USER_ID = "brandon_hancock"
    SESSION_ID = str(uuid.uuid4())

    # ✅ AWAIT session creation
    await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )

    print(f"CREATED NEW SESSION: {SESSION_ID}")

    runner = Runner(
        agent=question_answer_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    new_message = types.Content(
        role="user",
        parts=[types.Part(text="What is Brandon's favorite TV show?")]
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

    # ✅ AWAIT get_session
    session = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    print("=== Final Session State ===")
    for k, v in session.state.items():
        print(f"{k}: {v}")

    
    await close_litellm_async_clients()

# ✅ Run async main
asyncio.run(main())