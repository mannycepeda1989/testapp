import streamlit as st
import re
import time
from datetime import datetime

# --- 1. Terminal Aesthetic CSS ---
def apply_hacker_styles():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000;
            color: #00FF41;
            font-family: 'Courier New', Courier, monospace;
        }
        @keyframes matrix-scroll {
            0% { background-position: 0% 0%; }
            100% { background-position: 0% 1000px; }
        }
        .stApp {
            background-image: linear-gradient(rgba(0, 255, 65, 0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 255, 65, 0.05) 1px, transparent 1px);
            background-size: 100% 50px, 50px 100%;
            animation: matrix-scroll 60s linear infinite;
        }
        @keyframes glitch {
            0% { transform: translate(0); }
            20% { transform: translate(-5px, 5px); }
            40% { transform: translate(-5px, -5px); }
            60% { transform: translate(5px, 5px); }
            80% { transform: translate(5px, -5px); }
            100% { transform: translate(0); }
        }
        .stError {
            animation: glitch 0.3s cubic-bezier(.25,.46,.45,.94) both infinite;
            border: 2px solid #ff0000 !important;
            background-color: #220000 !important;
            color: #ff0000 !important;
        }
        .terminal-box {
            border: 1px solid #00FF41;
            padding: 20px;
            background: rgba(0, 20, 0, 0.9);
            box-shadow: 0 0 15px #00FF41;
            margin-bottom: 25px;
        }
        .stTextInput input {
            background-color: #000 !important;
            color: #00FF41 !important;
            border: 1px solid #00FF41 !important;
            font-family: 'Courier New', monospace !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #00FF41;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. Mission Database ---
MISSIONS = [
    {"lvl": 1, "task": "List all files in the current directory.", "valid": [r"^ls$"], "hint": "ls", "exp": "Command: ls"},
    {"lvl": 2, "task": "List all files, including hidden files.", "valid": [r"^ls\s+-a$", r"^ls\s+-la$"], "hint": "ls -a", "exp": "Command: ls -a"},
    {"lvl": 3, "task": "Create a new directory named 'backup'.", "valid": [r"^mkdir\s+backup$"], "effect": "📁 backup/", "hint": "mkdir backup", "exp": "Directory created."},
    {"lvl": 4, "task": "Change directory into the 'backup' folder.", "valid": [r"^cd\s+backup$"], "hint": "cd backup", "exp": "Directory changed."},
    {"lvl": 5, "task": "Print the current working directory path.", "valid": [r"^pwd$"], "hint": "pwd", "exp": "Path displayed."},
    {"lvl": 6, "task": "Move up one level to the parent directory.", "valid": [r"^cd\s+\.\.$"], "hint": "cd ..", "exp": "Moved to parent."},
    {"lvl": 7, "task": "Create an empty file named 'logs.txt'.", "valid": [r"^touch\s+logs\.txt$"], "effect": "📄 logs.txt", "hint": "touch logs.txt", "exp": "File created."},
    {"lvl": 8, "task": "Rename 'logs.txt' to 'old_logs.txt'.", "valid": [r"^mv\s+logs\.txt\s+old_logs\.txt$"], "effect": "📄 old_logs.txt", "hint": "mv [old] [new]", "exp": "File renamed."},
    {"lvl": 9, "task": "Copy 'old_logs.txt' to a new file 'logs_copy.txt'.", "valid": [r"^cp\s+old_logs\.txt\s+logs_copy\.txt$"], "effect": "📄 logs_copy.txt", "hint": "cp [src] [dest]", "exp": "File copied."},
    {"lvl": 10, "task": "Delete the file 'logs_copy.txt'.", "valid": [r"^rm\s+logs_copy\.txt$"], "hint": "rm logs_copy.txt", "exp": "File removed."},
    {"lvl": 11, "task": "Print the string 'hello' to the terminal.", "valid": [r"^echo\s+hello$"], "hint": "echo hello", "exp": "String printed."},
    {"lvl": 12, "task": "Search for the string 'error' inside 'sys.log'.", "valid": [r"^grep\s+error\s+sys\.log$"], "hint": "grep error sys.log", "exp": "Search complete."},
    {"lvl": 13, "task": "Display the first 10 lines of 'sys.log'.", "valid": [r"^head\s+sys\.log$"], "hint": "head sys.log", "exp": "File head displayed."},
    {"lvl": 14, "task": "Display the last 5 lines of 'sys.log'.", "valid": [r"^tail\s+-n\s+5\s+sys\.log$", r"^tail\s+-5\s+sys\.log$"], "hint": "tail -n 5 sys.log", "exp": "File tail displayed."},
    {"lvl": 15, "task": "Clear all text from the terminal screen.", "valid": [r"^clear$"], "hint": "clear", "exp": "Screen cleared."},
    {"lvl": 16, "task": "Open the manual page for the 'ls' command.", "valid": [r"^man\s+ls$"], "hint": "man ls", "exp": "Manual opened."},
    {"lvl": 17, "task": "Change 'script.sh' permissions to be executable.", "valid": [r"^chmod\s+\+x\s+script\.sh$"], "hint": "chmod +x script.sh", "exp": "Permissions updated."},
    {"lvl": 18, "task": "Check network connectivity to 'google.com'.", "valid": [r"^ping\s+google\.com$"], "hint": "ping google.com", "exp": "Ping response received."},
    {"lvl": 19, "task": "Display current network interface configurations.", "valid": [r"^ifconfig$", r"^ip\s+addr$"], "hint": "ifconfig", "exp": "Network data displayed."},
    {"lvl": 20, "task": "Display all currently running system processes.", "valid": [r"^top$", r"^ps\s+aux$"], "hint": "top", "exp": "Process list active."},
    {"lvl": 21, "task": "Create a zip archive 'archive.zip' of the 'backup' folder.", "valid": [r"^zip\s+archive\.zip\s+backup$"], "effect": "📦 archive.zip", "hint": "zip archive.zip backup", "exp": "Archive created."},
    {"lvl": 22, "task": "Find all files ending in '.txt' in the current directory.", "valid": [r"^find\s+\.\s+-name\s+\"\*\.txt\"$"], "hint": "find . -name \"*.txt\"", "exp": "Files located."},
    {"lvl": 23, "task": "List files and pipe the output to count the lines.", "valid": [r"^ls\s*\|\s*wc\s+-l$"], "hint": "ls | wc -l", "exp": "Line count returned."},
    {"lvl": 24, "task": "Read 'sys.log' and pipe output to search for 'warn'.", "valid": [r"^cat\s+sys\.log\s*\|\s*grep\s+warn$"], "hint": "cat sys.log | grep warn", "exp": "Filtered output displayed."},
    {"lvl": 25, "task": "Search 'sys.log' for 'error' and redirect output to 'errors.txt'.", "valid": [r"^grep\s+error\s+sys\.log\s*>\s*errors\.txt$"], "effect": "📄 errors.txt", "hint": "grep error sys.log > errors.txt", "exp": "Output redirected to file."}
]

# --- 3. Session State ---
if 'lvl_idx' not in st.session_state: st.session_state.lvl_idx = 0
if 'fs' not in st.session_state: st.session_state.fs = ["📁 root/", "📄 .env", "📄 sys.log", "📄 script.sh"]
if 'health' not in st.session_state: st.session_state.health = 5
if 'success_phase' not in st.session_state: st.session_state.success_phase = False
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()

# --- 4. UI Rendering ---
apply_hacker_styles()

with st.sidebar:
    st.markdown("### SYSTEM STATUS")
    st.metric("INTEGRITY", f"{st.session_state.health} HP")
    st.progress(st.session_state.lvl_idx / len(MISSIONS))
    st.write(f"Level: {st.session_state.lvl_idx + 1} / 25")
    st.divider()
    st.write("**VIRTUAL DRIVE**")
    for item in st.session_state.fs:
        st.caption(f"> {item}")
    if st.button("RESET GAME"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.title("TERMINAL HERO: SEC-OPS EDITION")

# Create the multi-tab interface
tab_game, tab_linux, tab_checkov, tab_cortex = st.tabs([
    "🎮 TERMINAL", 
    "📂 LINUX REF", 
    "🛡️ CHECKOV", 
    "☁️ CORTEX CLI"
])

with tab_linux:
    st.markdown("### Common Linux Commands")
    st.code("Files: ls, mkdir, touch, cp, mv, rm, find\nNav: cd, pwd\nContent: grep, cat, head, tail, echo\nSystem: chmod, ping, ifconfig, top, man\nOperators: | (pipe), > (redirect)")

with tab_checkov:
    st.markdown("### Checkov Infrastructure-as-Code (IaC) Reference")
    st.info("Checkov is used to scan Terraform, CloudFormation, and Kubernetes for security misconfigurations.")
    st.markdown("""
    | Parameter | Description |
    | :--- | :--- |
    | `-d [dir]` | Scan a specific directory. |
    | `-f [file]` | Scan a specific file. |
    | `--check [ID]` | Only run specific check (e.g., CKV_AWS_1). |
    | `--skip-check [ID]` | Exclude specific checks. |
    | `--quiet` | Only display failed checks. |
    | `--framework [type]` | Specify framework (terraform, cloudformation, kubernetes, all). |
    | `-o [format]` | Output format (cli, json, junitxml, github_failed_only, sarif). |
    | `--soft-fail` | Runs scans but returns a 0 exit code (useful for CI/CD pipelines). |
    """)

with tab_cortex:
    st.markdown("### Cortex CLI / Cortex Cloud Reference")
    st.info("Reference for managing Cortex Cloud environments and security findings.")
    st.markdown("""
    | Command / Parameter | Description |
    | :--- | :--- |
    | `cortex auth login` | Authenticate with the Cortex Cloud environment. |
    | `cortex conf` | View or modify local configurations. |
    | `--sarif [file]` | Path to the SARIF file for vulnerability ingestion. |
    | `cortex scan` | Initiate a scan of the target environment. |
    | `--project [ID]` | Specify the Cortex project ID. |
    | `--env [name]` | Specify target environment (prod, dev, staging). |
    | `-v` | Verbose output for debugging connection or parsing issues. |
    """)

with tab_game:
    if st.session_state.health <= 0:
        st.error("SYSTEM HALTED: TOO MANY ERRORS")
        if st.button("RESTART SYSTEM"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
    elif st.session_state.lvl_idx >= len(MISSIONS):
        st.balloons()
        st.header("TRAINING COMPLETE")
        duration = round(time.time() - st.session_state.start_time, 2)
        st.success(f"Final Time: {duration} seconds.")
        st.download_button("DOWNLOAD CERTIFICATE", "SEC-OPS CLI TRAINER COMPLETION", "cert.txt")
    else:
        current = MISSIONS[st.session_state.lvl_idx]
        st.markdown(f'<div class="terminal-box"><b>LEVEL {current["lvl"]}</b><br>{current["task"]}</div>', unsafe_allow_html=True)
        if st.button("SHOW HINT"):
            st.toast(f"HINT: {current['hint']}")
        
        cmd = st.text_input("user@terminal:~$ ", key=f"q_{st.session_state.lvl_idx}").strip()

        if not st.session_state.success_phase:
            if st.button("RUN COMMAND"):
                if any(re.match(p, cmd.lower()) for p in current['valid']):
                    st.session_state.success_phase = True
                    if "effect" in current: st.session_state.fs.append(current['effect'])
                    st.rerun()
                else:
                    st.error("SYNTAX ERROR")
                    st.session_state.health -= 1
                    st.rerun()
        else:
            st.success(f"CORRECT: {current['exp']}")
            if st.button("CONTINUE ➡️"):
                st.session_state.lvl_idx += 1
                st.session_state.success_phase = False
                st.rerun()
