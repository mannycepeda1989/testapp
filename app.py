import streamlit as st
import re
import time
from datetime import datetime

# --- 1. Game Data (25 Missions) ---
MISSIONS = [
    {"lvl": 1, "task": "List files in the current directory.", "valid": [r"^ls$"], "exp": "ls = list."},
    {"lvl": 2, "task": "List ALL files, including hidden ones.", "valid": [r"^ls\s+-a$", r"^ls\s+-la$"], "exp": "-a stands for 'all'."},
    {"lvl": 3, "task": "Create a directory named 'backup'.", "valid": [r"^mkdir\s+backup$"], "effect": "📁 backup/", "exp": "mkdir = make directory."},
    {"lvl": 4, "task": "Enter the 'backup' directory.", "valid": [r"^cd\s+backup$"], "exp": "cd = change directory."},
    {"lvl": 5, "task": "Show the path of your current directory.", "valid": [r"^pwd$"], "exp": "pwd = print working directory."},
    {"lvl": 6, "task": "Go back to the parent directory.", "valid": [r"^cd\s+\.\.$"], "exp": ".. represents the folder above you."},
    {"lvl": 7, "task": "Create a file named 'logs.txt'.", "valid": [r"^touch\s+logs\.txt$"], "effect": "📄 logs.txt", "exp": "touch creates empty files."},
    {"lvl": 8, "task": "Rename 'logs.txt' to 'old_logs.txt'.", "valid": [r"^mv\s+logs\.txt\s+old_logs\.txt$"], "effect": "📄 old_logs.txt", "exp": "mv = move (also used for renaming)."},
    {"lvl": 9, "task": "Copy 'old_logs.txt' to 'logs_copy.txt'.", "valid": [r"^cp\s+old_logs\.txt\s+logs_copy\.txt$"], "effect": "📄 logs_copy.txt", "exp": "cp = copy."},
    {"lvl": 10, "task": "Remove the file 'logs_copy.txt'.", "valid": [r"^rm\s+logs_copy\.txt$"], "exp": "rm = remove."},
    {"lvl": 11, "task": "Display the word 'hello' in the terminal.", "valid": [r"^echo\s+hello$"], "exp": "echo prints text to the screen."},
    {"lvl": 12, "task": "Search for 'error' in 'sys.log'.", "valid": [r"^grep\s+error\s+sys\.log$"], "exp": "grep is a powerful pattern search tool."},
    {"lvl": 13, "task": "Show the start of 'sys.log'.", "valid": [r"^head\s+sys\.log$"], "exp": "head shows the start of a file."},
    {"lvl": 14, "task": "Show the last 5 lines of 'sys.log'.", "valid": [r"^tail\s+-n\s+5\s+sys\.log$", r"^tail\s+-5\s+sys\.log$"], "exp": "tail shows the end of a file."},
    {"lvl": 15, "task": "Clear the terminal screen.", "valid": [r"^clear$"], "exp": "clear wipes the terminal view."},
    {"lvl": 16, "task": "Display the manual for 'ls'.", "valid": [r"^man\s+ls$"], "exp": "man = manual. Your best friend for learning."},
    {"lvl": 17, "task": "Make 'script.sh' executable.", "valid": [r"^chmod\s+\+x\s+script\.sh$"], "exp": "chmod changes permissions."},
    {"lvl": 18, "task": "Check connection to 'google.com'.", "valid": [r"^ping\s+google\.com$"], "exp": "ping tests network connectivity."},
    {"lvl": 19, "task": "Display network interface info.", "valid": [r"^ifconfig$", r"^ip\s+addr$"], "exp": "ifconfig shows IP details."},
    {"lvl": 20, "task": "Show running processes.", "valid": [r"^top$", r"^ps\s+aux$"], "exp": "top/ps show active tasks."},
    {"lvl": 21, "task": "Zip the 'backup' folder into 'archive.zip'.", "valid": [r"^zip\s+archive\.zip\s+backup$"], "effect": "📦 archive.zip", "exp": "zip compresses data."},
    {"lvl": 22, "task": "Find all .txt files in current folder.", "valid": [r"^find\s+\.\s+-name\s+\"\*\.txt\"$"], "exp": "find is for deep searches."},
    {"lvl": 23, "task": "BOSS: List files and count the lines.", "valid": [r"^ls\s*\|\s*wc\s+-l$"], "exp": "wc -l counts lines in piped output."},
    {"lvl": 24, "task": "BOSS: Cat 'sys.log' and grep for 'warn'.", "valid": [r"^cat\s+sys\.log\s*\|\s*grep\s+warn$"], "exp": "Chaining cat and grep is a pro move."},
    {"lvl": 25, "task": "FINAL BOSS: Grep 'error' in 'sys.log' and save to 'errors.txt'.", "valid": [r"^grep\s+error\s+sys\.log\s*>\s*errors\.txt$"], "effect": "📄 errors.txt", "exp": "'>' redirects output to a file."}
]

# --- 2. Session State ---
if 'lvl_idx' not in st.session_state:
    st.session_state.lvl_idx = 0
if 'fs' not in st.session_state:
    st.session_state.fs = ["📁 root/", "📄 .env", "📄 sys.log", "📄 script.sh"]
if 'health' not in st.session_state:
    st.session_state.health = 5
if 'success_phase' not in st.session_state:
    st.session_state.success_phase = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

# --- 3. Sidebar ---
with st.sidebar:
    st.title("📂 System Status")
    st.metric("Health", f"{st.session_state.health} HP")
    st.progress(st.session_state.lvl_idx / len(MISSIONS))
    st.write(f"Mission: {st.session_state.lvl_idx + 1} / {len(MISSIONS)}")
    st.divider()
    st.write("**Virtual Drive Contents:**")
    for item in st.session_state.fs:
        st.caption(item)
    if st.button("Factory Reset Game"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- 4. Main UI with Tabs ---
st.title("🕹️ Terminal Hero")

tab_game, tab_help = st.tabs(["🎮 Play Quest", "📖 Command Manual"])

with tab_help:
    st.header("Terminal Command Reference")
    st.markdown("""
    ### Navigation
    * `ls`: List files | `ls -a`: List all (including hidden)
    * `cd [dir]`: Change directory | `cd ..`: Go up
    * `pwd`: Print working directory path
    
    ### File Operations
    * `mkdir [name]`: Create folder | `touch [name]`: Create file
    * `cp [src] [dest]`: Copy | `mv [src] [dest]`: Move/Rename
    * `rm [file]`: Delete file | `chmod +x`: Make executable
    
    ### Tools & Filtering
    * `grep [text] [file]`: Search text | `cat [file]`: Read file
    * `head`: Top of file | `tail`: Bottom of file
    * `echo`: Print to screen | `man`: Command manual
    
    ### Advanced
    * `|` (Pipe): Pass output from one command to another.
    * `>` (Redirect): Save command output into a file.
    """)

with tab_game:
    if st.session_state.health <= 0:
        st.error("💀 KERNEL PANIC: System failure. Too many syntax errors.")
        if st.button("Reboot System"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    elif st.session_state.lvl_idx >= len(MISSIONS):
        duration = round(time.time() - st.session_state.start_time, 2)
        st.balloons()
        st.header("🏆 System Admin Status Achieved!")
        rank = "Kernel Overlord" if st.session_state.health >= 4 else "Bash Scripter"
        st.subheader(f"Rank: {rank} | Time: {duration}s")
        cert = f"CERTIFICATE OF CLI MASTERY\nRank: {rank}\nTime: {duration}s\nDate: {datetime.now()}"
        st.download_button("💾 Download Certification", cert, "cli_expert.txt")

    else:
        current = MISSIONS[st.session_state.lvl_idx]
        if current['lvl'] >= 23: st.warning("🔥 BOSS LEVEL")
        st.info(f"**TASK:** {current['task']}")
        
        cmd = st.text_input("admin@terminal:~$ ", key=f"q_{st.session_state.lvl_idx}").strip()

        if not st.session_state.success_phase:
            if st.button("Execute Command"):
                if any(re.match(p, cmd.lower()) for p in current['valid']):
                    st.session_state.success_phase = True
                    if "effect" in current: st.session_state.fs.append(current['effect'])
                    st.rerun()
                else:
                    st.error("Invalid command or syntax error.")
                    st.session_state.health -= 1
                    st.rerun()
        else:
            st.success(f"Correct! {current['exp']}")
            if st.button("Next Mission ➡️"):
                st.session_state.lvl_idx += 1
                st.session_state.success_phase = False
                st.rerun()
