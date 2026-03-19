import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. Page Configuration ---
st.set_page_config(page_title="GCP DevOps Quiz", page_icon="☁️", layout="centered")

# --- 2. AI Tutor Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("🔑 Please add your GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. Session State Management ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'answered' not in st.session_state: st.session_state.answered = False
if 'explanation' not in st.session_state: st.session_state.explanation = ""
if 'quiz_df' not in st.session_state: st.session_state.quiz_df = None

def reset_quiz():
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.explanation = ""
    # We don't reset quiz_df here so the shuffle persists until a new file is uploaded

# --- 4. Main UI ---
st.title("☁️ GCP Professional DevOps Exam Prep")

# Shuffle Toggle
do_shuffle = st.checkbox("Shuffle Questions", value=False, help="Randomize the question order before starting.")

uploaded_file = st.file_uploader("Upload your Question Bank (CSV)", type="csv")

if uploaded_file:
    # Load and Shuffle logic
    if st.session_state.quiz_df is None:
        df = pd.read_csv(uploaded_file)
        if do_shuffle:
            df = df.sample(frac=1).reset_index(drop=True)
        st.session_state.quiz_df = df

    df = st.session_state.quiz_df
    total_q = len(df)

    if st.session_state.idx < total_q:
        row = df.iloc[st.session_state.idx]
        
        st.write(f"### Question {st.session_state.idx + 1} of {total_q}")
        st.info(row['Question'])
        
        options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
        user_choice = st.radio("Choose the best answer:", options, index=None, key=f"q_{st.session_state.idx}")

        if st.button("Check Answer") and user_choice and not st.session_state.answered:
            correct_val = str(row['Correct Answer']).strip()
            st.session_state.answered = True
            
            if user_choice == correct_val:
                st.success(f"🎯 Correct! The answer is: {correct_val}")
                st.session_state.score += 1
            else:
                st.error(f"❌ Incorrect. The correct answer was: {correct_val}")
                
                with st.spinner("AI Tutor is analyzing..."):
                    prompt = f"Context: GCP Professional DevOps Engineer Exam. Question: {row['Question']} User chose: {user_choice} Correct answer: {correct_val}. Explain why the user is wrong and the correct one is best."
                    response = model.generate_content(prompt)
                    st.session_state.explanation = response.text

        if st.session_state.explanation:
            st.markdown("---")
            st.markdown(f"**💡 Tutor Insight:**\n\n{st.session_state.explanation}")

        if st.session_state.answered:
            if st.button("Next Question →"):
                st.session_state.idx += 1
                st.session_state.answered = False
                st.session_state.explanation = ""
                st.rerun()

    else:
        st.balloons()
        st.header("🏁 Quiz Finished!")
        st.metric("Final Score", f"{st.session_state.score} / {total_q}")
        if st.button("Restart Quiz"):
            st.session_state.quiz_df = None # Clear data so it can re-shuffle on restart
            reset_quiz()
            st.rerun()
else:
    st.session_state.quiz_df = None
    st.info("Upload a CSV file to begin.")