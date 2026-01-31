from fastapi import FastAPI, Request, Form, HTTPException , Body
from fastapi.responses import HTMLResponse , RedirectResponse , FileResponse
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import urllib.parse
import uuid
import asyncio
from typing import List
from google.adk.agents import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.events import Event, EventActions
from litellm import close_litellm_async_clients
from datetime import datetime
import time
from ..question_generation_agent import create_question_generation_agent
import json
from ..utils import (
    normalize_phase_2_questions,
    render_phase3_design_to_word,
    build_new_message_phase2,
    build_new_message_phase3
)
from ..design_document_agent import create_design_document_agent
from docx2pdf import convert
from litellm.exceptions import BadRequestError



app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory="design_engine/static"),
    name="static"
)


BASE_PATH = Path("design_engine/documents")

user_projects = {
    user_dir.name: [
        file.name
        for file in user_dir.iterdir()
        if file.is_file() and file.suffix.lower() == ".pdf"
    ]
    for user_dir in BASE_PATH.iterdir()
    if user_dir.is_dir()
}

print(f'All the user_projects are: {user_projects}')


templates = Jinja2Templates(directory="design_engine/templates")


sessions = {}

phase2_sessions = {}
session_service_stateful = InMemorySessionService()



@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )



@app.post("/login")
async def login(
    username: str = Form(...),
    password: int = Form(...)
):
    print(f'Username is {username} and type is {type(username)}')
    print(f'Password is {password} and type is {type(password)}')
    
    response = RedirectResponse(
            url="/dashboard",
            status_code=303
        )

        # 🍪 SEND COOKIE TO BROWSER
    response.set_cookie(
            key="user",
            value=username,
            httponly=True
        )

    return response



@app.post("/logout")
async def logout(request: Request, payload: dict = Body(...)):
    cookie_username = request.cookies.get("user_name")
    body_username = payload.get("username")

    if cookie_username != body_username:
        return {"error": "Invalid logout request"}

    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="user_name", path="/")
    return response

@app.get("/dashboard")
async def dashboard(request: Request):
    user = request.cookies.get("user")
    if not user:
        return HTMLResponse("<h3>You are not logged in</h3>", status_code=401)
    
    projects = user_projects.get(user, [])
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user, "projects": projects})



@app.get("/view-project/{username}/{project_name}")
async def view_project(username: str, project_name: str):
    filename = urllib.parse.unquote(project_name)

    base_path = Path("design_engine/documents") / username
    file_path = base_path / filename

    if file_path.exists() and file_path.suffix.lower() == ".pdf":
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{filename}"'
            }
        )

    raise HTTPException(status_code=404, detail="Project file not found")



@app.get("/new-project", response_class=HTMLResponse)
async def new_project_form(request: Request):
    return templates.TemplateResponse("new_project_phase1.html", {"request": request})


# ----------------------------
# Defining Global Agents
# ---------------------------
root_agent = SequentialAgent(
        name="design_engine",
        sub_agents=[create_question_generation_agent()],
        description=(
            "Pipeline: Phase 1 collects initial inputs, "
            "Phase 2 generates clarification questions."
        ),
    )



# ---------------------------
# Phase 1: Handle Form Submission
# ---------------------------
@app.post("/new-project-phase1")
async def new_project_phase1(
    request: Request,
    project_name: str = Form(...),
    project_type: str = Form(...),
    platform: str = Form(...),
    description: str = Form(...),
    core_features: str = Form(""),
    expected_user_scale: str = Form(...),
    constraints: List[str] = Form([])
):
    user = request.cookies.get("user")
    if not user:
        return HTMLResponse("Not logged in", status_code=401)

    phase_1_inputs = {
        "project_name": project_name,
        "project_type": project_type,
        "platform": platform,
        "description": description,
        "core_features": [f.strip() for f in core_features.split(",") if f.strip()],
        "expected_user_scale": expected_user_scale,
        "constraints": constraints,
        "user": user,
    }

    print(f'Phase1 inputs: {phase_1_inputs}')
    encoded = urllib.parse.quote(json.dumps(phase_1_inputs))

    # Redirect to Phase 2 questions (you can generate questions dynamically here)
    return RedirectResponse(f"/phase2?data={encoded}", status_code=303)


@app.get("/phase2")
async def phase2_start(request: Request, data: str = None):
    print(f'################### Inside Phase2 ############################')

    
    MAX_RETRIES = 5
    attempt = 0
    success = False
    phase_1_inputs = json.loads(urllib.parse.unquote(data)) if data else {}
    print(f'Phase1 inputs: {phase_1_inputs}')
    # Generate a session
    session_id = str(uuid.uuid4())
    print(f'Session ID:- {session_id}' )

    initial_state = {"phase_1_inputs": phase_1_inputs}
    print(f'Initial State:- {initial_state}')
    

    
    await session_service_stateful.create_session(
        app_name=phase_1_inputs["project_name"],
        user_id=phase_1_inputs["user"],
        session_id=session_id,
        state=initial_state
    )

    print(f'Session Created')


    runner = Runner(
        agent=root_agent,
        app_name=phase_1_inputs["project_name"],
        session_service=session_service_stateful,
    )
    print(f'Runner Created')

    new_message = types.Content(
        role="user",
        parts=[types.Part(
            text="Based on Phase 1 inputs, generate clarification questions to finalize the system design."
        )]
    )
    print(f'New Message Created')

    while attempt < MAX_RETRIES and not success:
        attempt += 1
        print(f"\n🔁 Runner attempt {attempt}")

        new_message = build_new_message_phase2(is_retry=(attempt > 1))

        try:
            async for event in runner.run_async(
                user_id=phase_1_inputs["user"],
                session_id=session_id,
                new_message=new_message,
            ):
                if event.is_final_response():
                    print("\n=== Phase 2 Questions Generated ===")
                    print(event.content.parts[0].text)
                    success = True

        except BadRequestError as e:
            print("❌ LLM BadRequestError occurred")
            print("Message:", str(e))

            if hasattr(e, "response"):
                print("Raw response:", e.response)

            if attempt >= MAX_RETRIES:
                print("🚨 Max retries reached. Aborting.")
                raise

            print("🔧 Retrying with stricter prompt...")

        except Exception as e:
            print("❌ Unexpected error:", e)
            raise

    
    # -----------------
    # Fetch Phase 2 Questions from Session
    # -----------------
    session = await session_service_stateful.get_session(
        app_name=phase_1_inputs["project_name"],
        user_id=phase_1_inputs["user"],
        session_id=session_id,
    )

    raw_phase_2_questions = session.state.get("phase_2_clarification_questions", {} )
    phase_2_clarification_questions = normalize_phase_2_questions( raw_phase_2_questions )


    phase2_sessions[session_id] = {
    "phase_1_inputs": phase_1_inputs,
    "questions": phase_2_clarification_questions["questions"],
    "question_keys": list(phase_2_clarification_questions["questions"].keys()),
    "current_index": 0,
    "answers": {}
    }


    print(phase_2_clarification_questions)

    return RedirectResponse(
    f"/phase2/{session_id}",
    status_code=303
    )



@app.get("/phase2/{session_id}")
async def phase2_question(request: Request, session_id: str):
    session = phase2_sessions.get(session_id)
    if not session:
        return HTMLResponse("Invalid session", status_code=404)

    idx = session["current_index"]
    question_text = session["question_keys"][idx]
    question_spec = session["questions"][question_text]

    return templates.TemplateResponse(
        "phase2/question.html",
        {
            "request": request,
            "session_id": session_id,
            "question": question_text,
            "options": question_spec["options"],
            "step": idx + 1,
            "total": len(session["question_keys"]),
            "is_last": idx == len(session["question_keys"]) - 1
        }
    )


@app.post("/phase2/{session_id}")
async def phase2_submit(
    request: Request,
    session_id: str,
    answers: list[str] = Form(...)
):
    session = phase2_sessions.get(session_id)
    if not session:
        return HTMLResponse("Invalid session", status_code=404)

    idx = session["current_index"]
    question_text = session["question_keys"][idx]

    form = await request.form()
    final_answers = []

    for ans in answers:
        if ans.lower() == "other":
            other_val = form.get("other_text")
            if other_val:
                final_answers.append(other_val)
        else:
            final_answers.append(ans)

    session["answers"][question_text] = final_answers
    session["current_index"] += 1

    # More questions?
    if session["current_index"] < len(session["question_keys"]):
        return RedirectResponse(
            f"/phase2/{session_id}",
            status_code=303
        )
    
    # ============================
    # 🎯 PHASE 2 COMPLETE
    # ============================
    phase_2_answers = session["answers"]
    app_name = session["phase_1_inputs"]["project_name"]
    user_id = session["phase_1_inputs"]["user"]

    # 🔐 Persist into session_service_stateful
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

    # You already created this earlier
    await session_service_stateful.append_event(
        await session_service_stateful.get_session(
            app_name=session["phase_1_inputs"]["project_name"],
            user_id=session["phase_1_inputs"]["user"],
            session_id=session_id,
        ),
        persist_event,
    )

    print("✅ Phase 2 answers persisted in session")

    # Cleanup in-memory cache (optional but recommended)
    del phase2_sessions[session_id]

    

    return RedirectResponse(f"/phase3/{session_id}/{app_name}/{user_id}", status_code=303)



@app.get("/phase3/{session_id}/{app_name}/{user_id}")
async def phase3_generate(request: Request, session_id: str , app_name: str , user_id: str):


        
    MAX_RETRIES = 5
    attempt = 0
    success = False
    
    # Fetch session
    session = await session_service_stateful.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    

    if not session:
        return HTMLResponse("Invalid session", status_code=404)
    

    

    print("📦 Session state entering Phase 3:")
    print(session.state)

    # -----------------
    # Phase 3 Agent
    # -----------------
    design_agent_runner = Runner(
        agent=SequentialAgent(
            name="design_engine_generation",
            sub_agents=[create_design_document_agent()]
        ),
        app_name=app_name,
        session_service=session_service_stateful,
    )

    design_message = types.Content(
        role="user",
        parts=[types.Part(
            text="Using all available session context (Phase 1 + Phase 2), generate the full system design document."
        )]
    )
    while attempt < MAX_RETRIES and not success:
        attempt += 1
        print(f"\n🔁 Runner attempt {attempt}")

        new_message = build_new_message_phase3(is_retry=(attempt > 1))
        try:
            async for event in design_agent_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=design_message,
            ):
                if event.is_final_response():
                    print("\n=== Phase 3 System Design Document ===")
                    print(event.content.parts[0].text)

        except BadRequestError as e:
            print("❌ LLM BadRequestError occurred")
            print("Message:", str(e))

            if hasattr(e, "response"):
                print("Raw response:", e.response)

            if attempt >= MAX_RETRIES:
                print("🚨 Max retries reached. Aborting.")
                raise

            print("🔧 Retrying with stricter prompt...")

        except Exception as e:
            print("❌ Unexpected error:", e)
            raise

    # -----------------
    # Fetch generated designexc
    # -----------------
    session = await session_service_stateful.get_session(
        app_name=app_name,
        user_id = user_id,
        session_id=session_id,
    )

    system_design_document = session.state.get("phase_3_system_design")

    # -----------------
    # Render to Word
    # -----------------
    output_word_path = f"design_engine/documents/{user_id}/{app_name}.docx"

    output_dir = Path(output_word_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    render_phase3_design_to_word(system_design_document, output_word_path)

    print(f"✅ System design document rendered: {output_word_path}")

    pdf_output_path = f"design_engine/documents/{user_id}/{app_name}.pdf"

    convert(
        output_word_path,
        pdf_output_path
    )

    user_projects.setdefault(user_id, []).append(app_name)

    projects = user_projects.get(user_id ,[])

    print(projects)

    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user_id, "projects": projects})


