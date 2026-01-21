from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
from pydantic import BaseModel, Field
from typing_extensions import Annotated

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


ollama_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
    api_base=OLLAMA_API_BASE
)

class EmailContent(BaseModel):
    subject: Annotated[
        str,
        Field(description="The subject of the email")
    ]
    body: Annotated[
        str,
        Field(description="The body content of the email")
    ]


root_agent = LlmAgent(
    name="email_agent",
    model=ollama_llm,
    output_schema=EmailContent,
    output_key="email_content",
    description="An agent that composes email content based on user input.",
    instruction="""
    You are an email composing agent. Given a user's request, generate an appropriate email subject and body.
    Ensure the email is professional and clear.
    
    Important: Return the output strictly in the specified JSON format without any additional text.
    Example Output:
    {
        "subject": "Meeting Reminder",
        "body": "Dear Team, This is a reminder for our meeting scheduled tomorrow at 10 AM. Please be prepared with your reports. Best regards, Manager"
    }

    """,
)