
# Part 1 Imports
import os
import asyncio
from dotenv import load_dotenv
import re
from google.adk.agents import LlmAgent , SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from .code_refactorer import code_refactorer
from .code_reviewer import code_reviewer
from .code_writer import code_writer

# Part 2 Constants and Env Setup
APP_NAME = "code_generation_pipeline_app"
USER_ID = "user_123"
SESSION_ID = "session_1"

load_dotenv()

# Set HF token
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")


# Part 3 Helper Functions
def extract_code(text: str) -> str:
    if not text:
        return ""

    for pattern in [r"```python(.*?)```", r"```(.*?)```"]:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return text.strip()

def save_code_to_file(code: str, filename: "test.py") -> None:
    try:
        with open(filename, "w") as file:
            file.write(code)
        print(f"Code saved to {filename}")
    except Exception as e:
        print(f"Error saving code to file: {e}")


# Part 4 Main Async Function
async def main():
    
    # Create pipeline agent
    pipeline = SequentialAgent(
        name="CodePipeline",
        sub_agents=[code_writer, code_reviewer, code_refactorer]
    )


    # Session service
    session_service = InMemorySessionService()

    # Create session
    await session_service.create_session(
        app_name=APP_NAME,
        session_id=SESSION_ID,
        user_id=USER_ID,
    )

    print("Active sessions:", session_service.sessions)

    # Runner
    agent_runner = Runner(
        app_name=APP_NAME,
        agent=pipeline,
        session_service=session_service,
    )

    # Chat loop
    while True:
        user_input = input("User: ")

        if user_input.lower() in {"exit", "quit"}:
            print("Exiting...")
            break

        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )

        final_event = None

        async for event in agent_runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content,
        ):
            
            # Optional: stream debug
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts)
                response_text = event.content.parts[0].text

        session = await session_service.get_session(
            app_name=APP_NAME,
            session_id=SESSION_ID,
            user_id=USER_ID,
        )
        
        state = session.state

        generated_code = state.get("generated_code", "")
        review_comments = state.get("review_comments", "")
        refactored_code = state.get("refactored_code", "")

        print("\n--- Pipeline Output ---")
        print("Generated Code:\n", generated_code)
        print("Review Comments:\n", review_comments)
        print("Refactored Code:\n", refactored_code)

        final_code = extract_code(refactored_code)
        save_code_to_file(final_code, "final_code.py")



if __name__ == "__main__":
    asyncio.run(main())
