import streamlit as st
import re
from datetime import datetime

# --- 1. Game Data ---
MISSIONS = [
    {
        "level": "1",
        "task": "List the contents of your directory.",
        "valid_patterns": [r"^ls$", r"^ls\s+-a$", r"^ls\s+-la$"],
        "explanation": "The 'ls' command (list) reveals files. Adding '-a' shows hidden files like .env!"
    },
    {
        "level": "2",
        "task": "Create a new directory named 'deploy'.",
        "valid_patterns": [r"^mkdir\s+deploy$"],
        "effect": "📁 deploy/",
        "explanation": "'mkdir' stands for 'make directory'. Use it to organize your project structure."
    },
    {
        "level": "3",
        "task": "Create an empty file named 'requirements.txt'.",
        "valid_patterns": [r"^touch\s+requirements\.txt$"],
        "effect": "📄 requirements.txt",
        "explanation": "'touch' is the standard way to create new, empty files instantly."
    },
    {
        "level": "BOSS",
        "task": "List all files and 'pipe' the output to find only 'requirements.txt'.",
        "valid_patterns": [r"^ls\s*\|\s*grep\s+requirements\.txt$"],
        "hint": "Try: ls | grep requirements.txt",
        "explanation": "You used a 'pipe' (|)! This passes the output of one command to another."
    }
]

# --- 2. Session State Management ---
if 'lvl_idx' not in st.session_state:
    st.session_state.lvl_idx = 0
if 'fs' not in st.session_state:
    st.session_state.fs = ["📁 root/", "📄 .env", "📄 README.md"]
if 'health' not in st.session_state:
    st.session_state.health = 3
if 'success_phase' not in st.session_state:
    st.session_state.success_phase = False

# --- 3. Sidebar (Filesystem View) ---
with st.sidebar:
    st.title("📂 System View")
    for item in st.session_state.fs:
        st.markdown(f"`{item}`")
    st.divider()
    st.metric("System Integrity", f"{st.session_state.health}/3 ❤️")
    if st.button("Reset Game"):
        st.session_state.lvl_idx = 0
        st.session_state.health = 3
        st.session_state.success_phase = False
        st.session_state.fs = ["📁 root/", "📄 .env", "📄 README.md"]
        st.rerun()

# --- 4. Main Game Logic ---
st.title("🖥️ Terminal Hero")

# Game Over Check
if st.session_state.health <= 0:
    st.error("🚫 SYSTEM CRASHED. Too many syntax errors.")
    if st.button("Reboot"):
        st.session_state.health = 3
        st.session_state.lvl_idx = 0
        st.rerun()

# Victory Check
elif st.session_state.lvl_idx >= len(MISSIONS):
    st.balloons()
    st.header("🏆 Kernel Master Certified!")
    cert_text = f"CLI EXPERT CERTIFICATE\nIssued: {datetime.now().strftime('%Y-%m-%d')}"
    st.download_button("💾 Download Certificate", cert_text, "cert.txt")

# Active Game
else:
    current = MISSIONS[st.session_state.lvl_idx]
    st.progress(st.session_state.lvl_idx / len(MISSIONS))
    
    if current['level'] == "BOSS":
        st.warning("⚠️ BOSS BATTLE")
    
    st.info(f"**GOAL:** {current['task']}")

    # The Terminal Input
    # We use a key that changes with the level index so it clears itself
    cmd = st.text_input("user@terminal:~$ ", key=f"input_{st.session_state.lvl_idx}").strip()

    # If the user hasn't succeeded yet, show the Execute button
    if not st.session_state.success_phase:
        if st.button("Execute"):
            is_valid = any(re.match(pattern, cmd.lower()) for pattern in current['valid_patterns'])
            if is_valid:
                st.session_state.success_phase = True
                if "effect" in current and current['effect'] not in st.session_state.fs:
                    st.session_state.fs.append(current['effect'])
                st.rerun()
            else:
                st.error("Bash: command not found.")
                st.session_state.health -= 1
                st.rerun()

    # If they succeeded, show the feedback and the Next button
    else:
        st.success("🎯 Success!")
        st.write(f"💡 {current['explanation']}")
        if st.button("Move to Next Mission ➡️"):
            st.session_state.lvl_idx += 1
            st.session_state.success_phase = False # Reset phase for next level
            st.rerun()
