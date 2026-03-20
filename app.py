import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. Page Configuration ---
st.set_page_config(page_title="GCP DevOps AI Quiz", page_icon="☁️", layout="centered")

# --- 2. AI Tutor Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Using 1.5-flash for speed and cost-efficiency
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ API Connection Error: {e}")
        st.stop()
else:
    st.error("🔑 Please add your GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. Session State Management ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'answered' not in st.session_state: st.session_state.answered = False
if 'explanation' not in st.session_state: st.session_state.explanation = ""
if 'is_correct' not in st.session_state: st.session_state.is_correct = False
if 'quiz_df' not in st.session_state: st.session_state.quiz_df = None

def reset_quiz():
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.explanation = ""
    st.session_state.is_correct = False
    st.session_state.quiz_df = None

# --- 4. Sidebar ---
with st.sidebar:
    st.header("Quiz Settings")
    do_shuffle = st.checkbox("Shuffle Questions", value=True)
    if st.button("Reset & Restart"):
        reset_quiz()
        st.rerun()

# --- 5. Main UI ---
st.title("☁️ GCP DevOps Professional Exam")
st.caption("AI-Powered Grading & Explanations")

uploaded_file = st.file_uploader("Upload gcp_full_bank.csv", type="csv")

if uploaded_file:
    if st.session_state.quiz_df is None:
        try:
            df = pd.read_csv(uploaded_file)
            # We only drop rows missing the Question text now
            df = df.dropna(subset=['Question'])
            if do_shuffle:
                df = df.sample(frac=1).reset_index(drop=True)
            st.session_state.quiz_df = df
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()

    df = st.session_state.quiz_df
    total_q = len(df)

    if st.session_state.idx < total_q:
        row = df.iloc[st.session_state.idx]
        
        st.write(f"### Question {st.session_state.idx + 1} of {total_q}")
        st.info(row['Question'])
        
        # Clean options for display
        options = [str(row['Option A']).strip(), 
                   str(row['Option B']).strip(), 
                   str(row['Option C']).strip(), 
                   str(row['Option D']).strip()]
        
        user_choice = st.radio("Select your answer:", options, index=None, key=f"radio_{st.session_state.idx}")

        if st.button("Check Answer") and user_choice and not st.session_state.answered:
            st.session_state.answered = True
            
            with st.spinner("AI Proctor is evaluating..."):
                try:
                    prompt = f"""
                    You are an expert GCP Professional DevOps Engineer exam proctor.
                    
                    Question: {row['Question']}
                    Options:
                    A: {row['Option A']}
                    B: {row['Option B']}
                    C: {row['Option C']}
                    D: {row['Option D']}
                    
                    The user chose: "{user_choice}"
                    
                    Task:
                    1. Determine if the user's choice is the single most correct answer according to Google Cloud best practices and SRE principles.
                    2. Provide a brief explanation of why it is correct or incorrect.
                    
                    Your response MUST start with either "RESULT: CORRECT" or "RESULT: INCORRECT" on the first line.
                    Followed by "EXPLANATION: " and your text.
                    """
                    
                    response = model.generate_content(prompt).text
                    
                    if "RESULT: CORRECT" in response:
                        st.session_state.is_correct = True
                        st.session_state.score += 1
                    else:
                        st.session_state.is_correct = False
                        
                    st.session_state.explanation = response.replace("RESULT: CORRECT", "").replace("RESULT: INCORRECT", "").replace("EXPLANATION:", "").strip()
                
                except Exception as e:
                    st.session_state.explanation = f"AI Service Error: {e}"

        # Display Feedback
        if st.session_state.answered:
            if st.session_state.is_correct:
                st.success("🎯 Correct!")
            else:
                st.error("❌ Incorrect")
            
            st.markdown(f"**Tutor Explanation:**\n{st.session_state.explanation}")
            
            if st.button("Next Question →"):
                st.session_state.idx += 1
                st.session_state.answered = False
                st.session_state.explanation = ""
                st.rerun()

    else:
        st.balloons()
        st.header("🏁 Exam Complete!")
        st.metric("Final Score", f"{st.session_state.score} / {total_q}")
        if st.button("Start Over"):
            reset_quiz()
            st.rerun()
else:
    st.info("Please upload your CSV to begin. The AI will handle the grading automatically.")
