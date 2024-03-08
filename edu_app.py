import json
import streamlit as st
from streamlit_tags import st_tags

from api_calls import (
    generate_qn,
    text_to_img
)

if "QN" not in st.session_state:
    st.session_state["QN"] = None

if "topics" not in st.session_state:
    st.session_state["topics"] = []

if "press_start" not in st.session_state:
    st.session_state["press_start"] = False

for key in ["NUM_QN", "NUM_CORRECT", "NUM_ATTEMPTS_CURRENT_QN"]:
    if key not in st.session_state:
        st.session_state[key] = 0

if "NUM_ATTEMPTS_PER_QN" not in st.session_state:
    st.session_state["NUM_ATTEMPTS_PER_QN"] = []

# Helper fn
def initialize_qn(topics):
    """ Generate a question and store it in the session state"""
    number_attempts = 0
    not_generated = True
    while (not_generated) & (number_attempts < 3):
        try:
            reply = generate_qn()
            reply = json.loads(reply)
            not_generated = False
            st.session_state["QN"] = reply
            st.session_state["NUM_QN"] += 1
        except Exception as e:
            number_attempts += 1
            st.toast(f"Failed to generate question. Retrying... ({number_attempts}/3). Error: {e}")
            continue

# Reset page
def reset_page():
    st.session_state["QN"] = None
    st.session_state["topic"] = None

def initialize_app():
    st.session_state["press_start"] = True

# UI
st.title('🍎 EasyLearn')
st.write("Welcome to EasyLearn! This app generates multiple choice questions for students to practice. It also provides a teacher's view to track student progress.")

if not st.session_state["press_start"]:
    st.session_state["topics"] = st_tags(label="What do you want to learn today?",
                                        text="Press to enter more")    

    st.button("Press to start", on_click=initialize_app)

if st.session_state["press_start"]:
    student_view, teacher_view = st.tabs(["Student View", "Teacher View"])

    with student_view:
        if st.session_state["QN"] is None:
            with st.spinner("Loading..."):
                initialize_qn(st.session_state["topics"])
                st.rerun()

        else:
            question_box = st.empty()

            reply = st.session_state["QN"]

            st.info("**QN:** " + reply['QN'])

            choices_box = st.empty()
            choice = choices_box.radio(label="Choose the correct option",
                            options=[reply['CHOICES'][str(i)] for i in range(1, 5)],
                            label_visibility="hidden",
                            horizontal=True)
            
            col1, col2 = st.columns(2)

            if col1.button("Submit ✅"):
                st.session_state["NUM_ATTEMPTS_CURRENT_QN"] += 1

                if choice == reply['CHOICES'][str(reply['Ans'])]:
                    st.success("Correct!", icon="🎉")
                    st.balloons()
                    with st.spinner("Generating image..."):
                        image = text_to_img(reply['CHOICES'][str(reply["Ans"])])
                        st.image(image, use_column_width=True)
                        st.session_state["NUM_CORRECT"] += 1
                        st.session_state["NUM_ATTEMPTS_PER_QN"].append(st.session_state["NUM_ATTEMPTS_CURRENT_QN"])
                        st.session_state["NUM_ATTEMPTS_CURRENT_QN"] = 0
                else:
                    st.warning("Try again!", icon="💪")
            
            col2.button("Generate another question 🔁", on_click=reset_page)

    with teacher_view:
        st.metric("Questions generated", st.session_state["NUM_QN"])
        st.metric("Questions correctly answered on first attempt", st.session_state["NUM_CORRECT"])
        try:
            st.metric("Average attempts per question", round(sum(st.session_state["NUM_ATTEMPTS_PER_QN"]) / len(st.session_state["NUM_ATTEMPTS_PER_QN"]), 2))
        except:
            pass
