import streamlit as st
import re
from datetime import datetime

# --- Game Data Configuration ---
MISSIONS = [
    {
        "level": 1,
        "task": "List the contents of your directory to see what files are here.",
        "valid_patterns": [r"^ls$", r"^ls\s-a$", r"^ls\s-la$"],
        "explanation": "The 'ls' command (list) reveals files. Adding '-a' shows hidden files like .env!"
    },
    {
        "level": 2,
        "task": "Create a new directory named 'deploy' for your project.",
        "valid_patterns": [r"^mkdir\s+deploy$"],
        "effect": "deploy/",
        "explanation": "'mkdir' stands for 'make directory'. It's essential for keeping your workspace clean."
    },
    {
        "level": 3,
        "task": "Create an empty file named 'requirements.txt'.",
        "valid_patterns": [r"^touch\s+requirements\.txt$"],
        "effect": "requirements.txt",
        "explanation": "'touch' is the fastest way to create a new file or update a timestamp."
    },
    {
        "level": "BOSS",
        "task": "BOSS BATTLE: List all files and 'pipe' the output to find only the 'requirements.txt' file.",
        "valid_patterns": [r"^ls\s*\|\s*grep\s+requirements\.txt$"],
        "hint": "Use the pipe symbol '|' to connect 'ls' and 'grep'.",
        "explanation": "You chained two programs! 'ls' outputted the list, and 'grep' filtered it for you."
    }
]

# --- Session State Initialization ---
if 'lvl_idx' not in st.session_state:
    st.session_state.lvl_idx = 0
if 'fs' not in st.session_state:
    st.session_state.fs = ["🏠 root/", "📄 .env", "📄 README.md"]
if 'health' not in st.session_state:
    st.session_state.health = 3
if 'game_complete' not in st.session_state:
    st.session_state.game_complete = False

# --- Sidebar: Visual Filesystem ---
with st.sidebar:
    st.title("📂 System Navigator")
    st.write("Current Workspace:")
    for item in st.session_state.fs:
        st.code(item)
    
    st.divider()
    st.metric("System Integrity", f"{st.session_state.health}/3 ❤️")
    
    if st.button("Emergency Reboot (Reset)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Main Game UI ---
st.title("🖥️ Terminal Hero: Command Quest")
st.caption("Master the CLI and save the system.")

if st.session_state.health <= 0:
    st.error("🚫 SYSTEM CRASHED. Too many syntax errors.")
    if st.button("Reinstall OS (Restart)"):
        st.session_state.lvl_idx = 0
        st.session_state.health = 3
        st.rerun()

elif not st.session_state.game_complete:
    current = MISSIONS[st.session_state.lvl_idx]
    
    # Progress UI
    progress = (st.session_state.lvl_idx) / len(MISSIONS)
    st.progress(progress)
    
    if current['level'] == "BOSS":
        st.warning("⚠️ BOSS LEVEL: COMMAND CHAINING")
    
    st.info(f"**LEVEL {current['level']} MISSION:** {current['task']}")
    
    if "hint" in current:
        with st.expander("Need a hint?"):
            st.write(current['hint'])

    # Terminal Input
    user_input = st.text_input("admin@streamlit:~$ ", placeholder="Type command...", key=f"in_{st.session_state.lvl_idx}")

    if st.button("Execute Command"):
        # Regex check for flexibility (ignoring case and extra spaces)
        is_correct = any(re.match(pattern, user_input.strip().lower()) for pattern in current['valid_patterns'])
        
        if is_correct:
            st.success("🎯 Success! Command accepted.")
            if "effect" in current and current['effect'] not in st.session_state.fs:
                st.session_state.fs.append(current['effect'])
            
            st.write(f"💡 **Expert Insight:** {current['explanation']}")
            
            if st.session_state.lvl_idx < len(MISSIONS) - 1:
                if st.button("Next Level ➡️"):
                    st.session_state.lvl_idx += 1
                    st.rerun()
            else:
                st.session_state.game_complete = True
                st.rerun()
        else:
            st.error("❌ Bash: command not found or incorrect flags.")
            st.session_state.health -= 1
            st.rerun()

else:
    # Victory Screen
    st.balloons()
    st.header("🏆 Kernel Master Certified!")
    st.success("You have successfully navigated the filesystem and mastered command piping.")
    
    # Generate Certificate Content
    cert_text = f"""
    ========================================
    CERTIFICATE OF COMMAND LINE EXPERTISE
    ========================================
    This certifies that the user has completed 
    the Terminal Hero Quest on {datetime.now().strftime('%Y-%m-%d')}.
    
    Skills Mastered:
    - Filesystem Navigation (ls, pwd)
    - Resource Management (mkdir, touch)
    - Command Piping (grep, |)
    ========================================
    """
    
    st.download_button(
        label="💾 Download Your Expert Certificate",
        data=cert_text,
        file_name="CLI_Expert_Certificate.txt",
        mime="text/plain"
    )
