import streamlit as st
import re
import time
from datetime import datetime

# --- 1. Custom CSS for Terminal Aesthetics ---
def local_css():
    st.markdown("""
        <style>
        /* Main background and font */
        .stApp {
            background-color: #0e1117;
        }
        /* Custom Terminal Box styling */
        .terminal-text {
            font-family: 'Courier New', Courier, monospace;
            color: #00ff00;
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.1);
            margin-bottom: 20px;
        }
        /* Styling the text input to look like a prompt */
        .stTextInput input {
            background-color: #000 !important;
            color: #00ff00 !important;
            font-family: 'Courier New', Courier, monospace !important;
            border: 1px solid #00ff00 !important;
        }
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #111;
            border-right: 1px solid #333;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 25-Mission Database ---
MISSIONS = [
    {"lvl": 1, "task": "List files in the current directory.", "valid": [r"^ls$"], "hint": "Short for 'list'.", "exp": "ls = list."},
    {"lvl": 2, "task": "List ALL files, including hidden ones.", "valid": [r"^ls\s+-a$", r"^ls\s+-la$"], "hint": "Use the -a flag.", "exp": "-a stands for 'all'."},
    {"lvl": 3, "task": "Create a directory named 'backup'.", "valid": [r"^mkdir\s+backup$"], "effect": "📁 backup/", "hint": "mkdir = make directory.", "exp": "mkdir = make directory."},
    {"lvl": 4, "task": "Enter the 'backup' directory.", "valid": [r"^cd\s+backup$"], "hint": "cd = change directory.", "exp": "cd = change directory."},
    {"lvl": 5, "task": "Show the path of your current directory.", "valid": [r"^pwd$"], "hint": "Print Working Directory.", "exp": "pwd = print working directory."},
    {"lvl": 6, "task": "Go back to the parent directory.", "valid": [r"^cd\s+\.\.$"], "hint": ".. refers to the folder above.", "exp": ".. is parent directory."},
    {"lvl": 7, "task": "Create a file named 'logs.txt'.", "valid": [r"^touch\s+logs\.txt$"], "effect": "📄 logs.txt", "hint": "Use 'touch'.", "exp": "touch creates files."},
    {"lvl": 8, "task": "Rename 'logs.txt' to 'old_logs.txt'.", "valid": [r"^mv\s+logs\.txt\s+old_logs\.txt$"], "effect": "📄 old_logs.txt", "hint": "mv = move/rename.", "exp": "mv renames files."},
    {"lvl": 9, "task": "Copy 'old_logs.txt' to 'logs_copy.txt'.", "valid": [r"^cp\s+old_logs\.txt\s+logs_copy\.txt$"], "effect": "📄 logs_copy.txt", "hint": "cp = copy.", "exp": "cp = copy."},
    {"lvl": 10, "task": "Remove the file 'logs_copy.txt'.", "valid": [r"^rm\s+logs_copy\.txt$"], "hint": "rm = remove.", "exp": "rm deletes files."},
    {"lvl": 11, "task": "Display the word 'hello' in the terminal.", "valid": [r"^echo\s+hello$"], "hint": "echo prints text.", "exp": "echo prints to screen."},
    {"lvl": 12, "task": "Search for 'error' in 'sys.log'.", "valid": [r"^grep\s+error\s+sys\.log$"], "hint": "Use 'grep'.", "exp": "grep searches patterns."},
    {"lvl": 13, "task": "Show the start of 'sys.log'.", "valid": [r"^head\s+sys\.log$"], "hint": "head shows the top.", "exp": "head = top of file."},
    {"lvl": 14, "task": "Show the last 5 lines of 'sys.log'.", "valid": [r"^tail\s+-n\s+5\s+sys\.log$", r"^tail\s+-5\s+sys\.log$"], "hint": "Use 'tail'.", "exp": "tail = end of file."},
    {"lvl": 15, "task": "Clear the terminal screen.", "valid": [r"^clear$"], "hint": "Typing 'clear' resets the view.", "exp": "clear wipes screen."},
    {"lvl": 16, "task": "Display the manual for 'ls'.", "valid": [r"^man\s+ls$"], "hint": "man = manual.", "exp": "man provides docs."},
    {"lvl": 17, "task": "Make 'script.sh' executable.", "valid": [r"^chmod\s+\+x\s+script\.sh$"], "hint": "chmod changes modes.", "exp": "chmod +x is for execution."},
    {"lvl": 18, "task": "Check connection to 'google.com'.", "valid": [r"^ping\s+google\.com$"], "hint": "Use 'ping'.", "exp": "ping tests network."},
    {"lvl": 19, "task": "Display network interface info.", "valid": [r"^ifconfig$", r"^ip\s+addr$"], "hint": "ifconfig or ip addr.", "exp": "ifconfig shows IPs."},
    {"lvl": 20, "task": "Show running processes.", "valid": [r"^top$", r"^ps\s+aux$"], "hint": "top or ps aux.", "exp": "top shows active tasks."},
    {"lvl": 21, "task": "Zip 'backup' into 'archive.zip'.", "valid": [r"^zip\s+archive\.zip\s+backup$"], "effect": "📦 archive.zip", "hint": "Use 'zip'.", "exp": "zip compresses data."},
    {"lvl": 22, "task": "Find all .txt files in current folder.", "valid": [r"^find\s+\.\s+-name\s+\"\*\.txt\"$"], "hint": "Use 'find . -name'.", "exp": "find is for searches."},
    {"lvl": 23, "task": "BOSS: List files and count the lines.", "valid": [r"^ls\s*\|\s*wc\s+-l$"], "hint": "Use '|' and 'wc -l'.", "exp": "wc -l counts lines."},
    {"lvl": 24, "task": "BOSS: Cat 'sys.log' and grep for 'warn'.", "valid": [r"^cat\s+sys\.log\s*\|\s*grep\s+warn$"], "hint": "Pipe cat into grep.", "exp": "Piping chains tools."},
    {"lvl": 25, "task": "FINAL BOSS: Grep 'error' in 'sys.log' and save to 'errors.txt'.", "valid": [r"^grep\s+error\s+sys\.log\s*>\s*errors\.txt$"], "effect": "📄 errors.txt", "hint": "Use '>' to redirect.", "exp": "'>' saves output to file."}
]

# --- 3. Session State ---
if 'lvl_idx' not in st.session_state:
    st.session_state.lvl_idx = 0
if 'fs' not in st.session_state:
    st.session_state.fs = ["📁 root/", "📄 .env", "📄 sys.log", "📄 script.sh"]
if 'health' not in st.session_state:
    st.session_state.health = 5
if 'success_phase' not in st.session_state:
    st.session_state.success_phase = False
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 4. Main UI Logic ---
local_css()

with st.sidebar:
    st.title("📟 OS KERNEL")
    st.metric("INTEGRITY", f"{st.session_state.health} HP")
    st.progress(st.session_state.lvl_idx / len(MISSIONS))
    st.divider()
    st.write("**DRIVE MAP:**")
    for item in st.session_state.fs:
        st.caption(item)
    st.divider()
    if st.button("FACTORY RESET"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.title("🖥️ TERMINAL HERO v1.0")

tab_game, tab_help = st.tabs(["🎮 LOGON", "📖 MANUAL"])

with tab_help:
    st.markdown("### 🔍 System Documentation")
    st.code("Navigation: ls, cd, pwd\nFiles: mkdir, touch, cp, mv, rm\nNetwork: ping, ifconfig\nPower: |, >, grep, wc")

with tab_game:
    if st.session_state.health <= 0:
        st.error("🚫 KERNEL PANIC: SYSTEM FAILURE")
        if st.button("REBOOT"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    elif st.session_state.lvl_idx >= len(MISSIONS):
        st.balloons()
        st.header("🏆 ROOT ACCESS GRANTED")
        st.success("You are now a Terminal Expert.")
        st.download_button("💾 DOWNLOAD CERT", "Expert CLI Certificate", "cert.txt")

    else:
        current = MISSIONS[st.session_state.lvl_idx]
        
        # Displaying the mission in a "Terminal Box"
        st.markdown(f"""
        <div class="terminal-text">
            <strong>SYSTEM MISSION {st.session_state.lvl_idx + 1}:</strong><br>
            {current['task']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💡 REQUEST HINT"):
            st.toast(f"HINT: {current['hint']}")
        
        cmd_input = st.text_input("admin@root:~$ ", key=f"q_{st.session_state.lvl_idx}").strip()

        if not st.session_state.success_phase:
            if st.button("EXECUTE"):
                st.session_state.history.append(cmd_input)
                # Check regex
                if any(re.match(p, cmd_input.lower()) for p in current['valid']):
                    st.session_state.success_phase = True
                    if "effect" in current and current['effect'] not in st.session_state.fs:
                        st.session_state.fs.append(current['effect'])
                    st.rerun()
                else:
                    st.error("SYNTAX ERROR")
                    st.session_state.health -= 1
                    st.rerun()
        else:
            st.success(f"COMMAND ACCEPTED: {current['exp']}")
            if st.button("NEXT LEVEL ➡️"):
                st.session_state.lvl_idx += 1
                st.session_state.success_phase = False
                st.rerun()

    # Console Output (History) at the bottom
    if st.session_state.history:
        with st.expander("CONSOLE LOGS"):
            for cmd in st.session_state.history[-10:]:
                st.text(f"Executed: {cmd}")
