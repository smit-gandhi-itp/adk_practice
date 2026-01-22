import os
import asyncio
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


load_dotenv()

# Set HF token
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")


async def main():
    # Initialize model
    hf_model = LiteLlm(
        "huggingface/together/deepseek-ai/DeepSeek-R1"
    )

    # Create agent
    base_agent = LlmAgent(
        name="general_purpose_agent",
        model=hf_model,
        description="A general purpose agent that can handle a variety of tasks.",
        instruction="""
        You are a versatile assistant. Based on the user's request,
        provide a helpful and accurate response.
        """
    )

    # Session service
    session_service = InMemorySessionService()

    # Create session
    await session_service.create_session(
        app_name="demo_app",
        session_id="session_1",
        user_id="user_123",
    )

    print("Active sessions:", session_service.sessions)

    # Runner
    agent_runner = Runner(
        app_name="demo_app",
        agent=base_agent,
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
            user_id="user_123",
            session_id="session_1",
            new_message=content,
        ):
            
            # Optional: stream debug
            print(event)

        print("final Response:", event.content.parts[1].text)


if __name__ == "__main__":
    asyncio.run(main())
