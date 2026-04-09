import streamlit as st
from llm import ask_llm
import prompts
from utils import (
    save_candidate_data,
    extract_candidate_info,
    save_answer
)

st.set_page_config(page_title="TalentScout Hiring Assistant", layout="centered")
st.title("🤖 TalentScout Hiring Assistant")

# -------------------------
# SESSION STATE
# -------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "greeting"

if "history" not in st.session_state:
    st.session_state.history = []

if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0


# -------------------------
# GREETING
# -------------------------
if st.session_state.stage == "greeting":
    response = ask_llm(prompts.greeting_prompt(), st.session_state.history)
    st.chat_message("assistant").write(response)
    st.session_state.history.append({"role": "assistant", "content": response})
    st.session_state.stage = "info"


# -------------------------
# CHAT INPUT
# -------------------------
user_input = st.chat_input("Type your response here...")

if user_input:
    # Show user message
    st.chat_message("user").write(user_input)
    st.session_state.history.append({"role": "user", "content": user_input})

    # Exit condition
    if user_input.lower() in ["exit", "quit", "bye", "end"]:
        response = ask_llm(prompts.end_prompt(), st.session_state.history)
        st.chat_message("assistant").write(response)
        st.session_state.history.append({"role": "assistant", "content": response})
        st.stop()

    # -------------------------
    # STAGE 1: COLLECT INFO
    # -------------------------
    if st.session_state.stage == "info":
        # Extract structured data
        parsed = extract_candidate_info(user_input)
        st.session_state.candidate_data.update(parsed)

        # Ask for tech stack next
        response = ask_llm(prompts.tech_stack_prompt(), st.session_state.history)
        st.chat_message("assistant").write(response)
        st.session_state.history.append({"role": "assistant", "content": response})

        st.session_state.stage = "tech"

    # -------------------------
    # STAGE 2: TECH STACK
    # -------------------------
    elif st.session_state.stage == "tech":
        st.session_state.candidate_data["tech_stack"] = user_input

        # Generate technical questions
        response = ask_llm(
            prompts.tech_questions_prompt(user_input),
            st.session_state.history
        )

        # Convert to list
        questions = [q.strip() for q in response.split("\n") if q.strip()]
        st.session_state.questions = questions
        st.session_state.current_question = 0

        st.chat_message("assistant").write("Great! Let's begin technical screening 👇")
        st.chat_message("assistant").write(st.session_state.questions[0])

        st.session_state.stage = "questions"

    # -------------------------
    # STAGE 3: QUESTIONS
    # -------------------------
    elif st.session_state.stage == "questions":
        # Save answer
        save_answer(
            st.session_state.candidate_data,
            st.session_state.current_question,
            user_input
        )

        # Optional: Evaluate answer
        feedback = ask_llm(
            prompts.evaluate_answer_prompt(
                st.session_state.questions[st.session_state.current_question],
                user_input
            ),
            st.session_state.history
        )

        st.chat_message("assistant").write(feedback)
        st.session_state.history.append({"role": "assistant", "content": feedback})

        # Move to next question
        st.session_state.current_question += 1

        if st.session_state.current_question < len(st.session_state.questions):
            next_q = st.session_state.questions[st.session_state.current_question]
            st.chat_message("assistant").write(next_q)
        else:
            # End process
            st.chat_message("assistant").write(
                "✅ Thank you! You’ve completed the screening."
            )

            # Save data
            save_candidate_data(st.session_state.candidate_data)

            # Final message
            end_msg = ask_llm(prompts.end_prompt(), st.session_state.history)
            st.chat_message("assistant").write(end_msg)

            st.session_state.stage = "done"

    # -------------------------
    # FALLBACK
    # -------------------------
    else:
        response = ask_llm(prompts.fallback_prompt(), st.session_state.history)
        st.chat_message("assistant").write(response)
        st.session_state.history.append({"role": "assistant", "content": response})