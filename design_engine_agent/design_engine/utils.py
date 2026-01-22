
# =========================
# Phase 1 – CLI Helpers
# =========================

def ask_text(question: str) -> str:
    print(f"\n{question}")
    return input("> ").strip()


def ask_single_choice(question: str, options: list[str]) -> str:
    print(f"\n{question}")
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")

    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("❌ Invalid choice. Please enter a valid number.")


def ask_multi_choice(question: str, options: list[str]) -> list[str]:
    print(f"\n{question}")
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")

    print("Enter comma-separated numbers (e.g. 1,3,5). Press Enter to skip.")

    while True:
        raw = input("> ").strip()
        if not raw:
            return []

        try:
            indexes = [int(i.strip()) for i in raw.split(",")]
            if all(1 <= i <= len(options) for i in indexes):
                return [options[i - 1] for i in indexes]
        except ValueError:
            pass

        print("❌ Invalid input. Try again.")


# =========================
# Phase 1 – Design Engine
# =========================

def run_phase_1_design_engine() -> dict:
    print("\n======================================")
    print(" Agentic Design Engine – Phase 1 ")
    print(" User Input & Context Setup ")
    print("======================================")

    project_name = ask_text("Project Name (e.g. Payment Gateway Platform)")

    project_type = ask_single_choice(
        "Project Type",
        [
            "Web Application",
            "Mobile Application",
            "Backend Service",
            "Data Platform",
            "ML / AI System",
            "Internal Tool",
        ],
    )

    platform = ask_single_choice(
        "Primary Platform",
        [
            "Web",
            "Mobile",
            "Backend / API",
            "Data / Analytics",
            "Mixed",
        ],
    )

    description = ask_text(
        "Project Description\nBriefly describe what this system does and why it exists"
    )

    core_features_raw = ask_text(
        "Core Features\nEnter comma-separated features (e.g. Auth, Payments, Reports)"
    )
    core_features = [f.strip() for f in core_features_raw.split(",") if f.strip()]

    expected_user_scale = ask_single_choice(
        "Expected User Scale",
        [
            "Prototype / Internal",
            "Up to 10k users",
            "10k - 100k users",
            "100k - 1M users",
            "1M+ users",
        ],
    )

    constraints = ask_multi_choice(
        "Primary Constraints",
        [
            "Performance",
            "Cost",
            "Security",
            "Compliance",
            "Time-to-market",
            "Scalability",
        ],
    )

    return {
        "project_name": project_name,
        "project_type": project_type,
        "platform": platform,
        "description": description,
        "core_features": core_features,
        "expected_user_scale": expected_user_scale,
        "constraints": constraints,
    }


# =========================
# Phase 2
# ========================



def run_phase_2_clarification_engine(phase_2_clarification_questions: dict) -> dict:
    print("\n======================================")
    print(" Agentic Design Engine - Phase 2 ")
    print(" Clarification Questions ")
    print("======================================")

    answers = {}

    questions = phase_2_clarification_questions.get("questions", {})

    for question_text, spec in questions.items():
        q_type = spec["type"]

        if q_type != "multi_choice":
            raise ValueError(
                f"Unsupported question type: {q_type}. "
                "Only multi_choice is allowed in this Phase 2 engine."
            )

        options = spec["options"]

        # Ask user to select one or more options
        selected = ask_multi_choice(question_text, options)

        # Robust check for "Other" selection
        if any("other" in choice.lower() for choice in selected):
            other_answer = ask_text(
                f"You selected 'Other' for the question:\n{question_text}\nPlease specify:"
            )
            # Replace any "Other" choice with the custom input
            selected = [
                other_answer if "other" in choice.lower() else choice for choice in selected
            ]

        answers[question_text] = selected

    return answers