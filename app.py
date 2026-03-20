import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. Page Configuration ---
st.set_page_config(page_title="GCP DevOps Quiz", page_icon="☁️", layout="centered")

# --- 2. AI Tutor Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Using the absolute path 'models/...' helps resolve the NotFound error
        # for keys created in standard Google Cloud projects.
        model_name = 'models/gemini-1.5-flash'
        model = genai.GenerativeModel(model_name)
        
        # Test connectivity and model existence
        # This list_models call confirms the key has the "Generative Language API" enabled
        available_models = [m.name for m in genai.list_models()]
        if model_name not in available_models:
             # Fallback to generic pro if flash isn't in the project's enabled list
             model = genai.GenerativeModel('gemini-pro')
             
    except Exception as e:
        st.error(f"❌ API Connection Error: {e}")
        st.info("Tip: Ensure 'Generative Language API' is enabled in your Google Cloud Console.")
        st.stop()
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
    st.session_state.quiz_df = None

# --- 4. Sidebar & Debugging ---
with st.sidebar:
    st.header("Settings")
    do_shuffle = st.checkbox("Shuffle Questions", value=False)
    if st.button("Reset Quiz"):
        reset_quiz()
        st.rerun()
    
    if st.checkbox("Show Debug Info"):
        st.write("Available Models:", [m.name.split('/')[-1] for m in genai.list_models()])

# --- 5. Main UI ---
st.title("☁️ GCP Professional DevOps Exam Prep")

uploaded_file = st.file_uploader("Upload your Question Bank (CSV)", type="csv")

if uploaded_file:
    # Load and Shuffle logic
    if st.session_state.quiz_df is None:
        try:
            df = pd.read_csv(uploaded_file)
            # Basic cleanup: remove empty rows that often happen in Excel exports
            df = df.dropna(subset=['Question', 'Correct Answer'])
            
            if do_shuffle:
                df = df.sample(frac=1).reset_index(drop=True)
            st.session_state.quiz_df = df
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            st.stop()

    df = st.session_state.quiz_df
    total_q = len(df)

    if st.session_state.idx < total_q:
        row = df.iloc[st.session_state.idx]
        
        st.write(f"### Question {st.session_state.idx + 1} of {total_q}")
        st.info(row['Question'])
        
        # Prepare options (stripping whitespace to ensure matching works)
        options = [str(row['Option A']).strip(), 
                   str(row['Option B']).strip(), 
                   str(row['Option C']).strip(), 
                   str(row['Option D']).strip()]
        
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
                    try:
                        prompt = f"""
                        Context: GCP Professional DevOps Engineer Exam.
                        Question: {row['Question']}
                        User chose: {user_choice}
                        Correct answer: {correct_val}
                        
                        Explain briefly why the user's choice is incorrect and why the correct choice is the best practice for GCP SRE/DevOps.
                        """
                        response = model.generate_content(prompt)
                        st.session_state.explanation = response.text
                    except Exception as e:
                        st.session_state.explanation = f"Could not reach AI Tutor: {e}"

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
            reset_quiz()
            st.rerun()
else:
    st.info("Please upload your file to begin.")
