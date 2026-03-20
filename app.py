import streamlit as st
import re
import time
from datetime import datetime

# --- 1. Custom Hollywood Hacker CSS ---
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

# --- 2. The Complete 25-Mission Database ---
MISSIONS = [
    {"lvl": 1, "task": "LIST FILES IN THE CURRENT DIRECTORY.", "valid": [r"^ls$"], "hint": "ls", "exp": "DIRECTORY ENUMERATED."},
    {"lvl": 2, "task": "IDENTIFY HIDDEN SYSTEM FILES.", "valid": [r"^ls\s+-a$", r"^ls\s+-la$"], "hint": "ls -a", "exp": "HIDDEN LAYERS REVEALED."},
    {"lvl": 3, "task": "INITIALIZE DIRECTORY: 'BACKUP'.", "valid": [r"^mkdir\s+backup$"], "effect": "📁 backup/", "hint": "mkdir backup", "exp": "STORAGE SECTOR CREATED."},
    {"lvl": 4, "task": "PENETRATE 'BACKUP' DIRECTORY.", "valid": [r"^cd\s+backup$"], "hint": "cd backup", "exp": "DIRECTORY ACCESSED."},
    {"lvl": 5, "task": "LOCATE CURRENT SYSTEM COORDINATES.", "valid": [r"^pwd$"], "hint": "pwd", "exp": "COORDINATES CONFIRMED."},
    {"lvl": 6, "task": "RETREAT TO PARENT NODE.", "valid": [r"^cd\s+\.\.$"], "hint": "cd ..", "exp": "UPLINK RESTORED."},
    {"lvl": 7, "task": "CREATE SYSTEM LOG FILE: 'LOGS.TXT'.", "valid": [r"^touch\s+logs\.txt$"], "effect": "📄 logs.txt", "hint": "touch logs.txt", "exp": "FILE INITIALIZED."},
    {"lvl": 8, "task": "RENAME 'LOGS.TXT' TO 'OLD_LOGS.TXT'.", "valid": [r"^mv\s+logs\.txt\s+old_logs\.txt$"], "effect": "📄 old_logs.txt", "hint": "mv [old] [new]", "exp": "RENAME SUCCESSFUL."},
    {"lvl": 9, "task": "CLONE 'OLD_LOGS.TXT' TO 'LOGS_COPY.TXT'.", "valid": [r"^cp\s+old_logs\.txt\s+logs_copy\.txt$"], "effect": "📄 logs_copy.txt", "hint": "cp [src] [dest]", "exp": "DATA CLONED."},
    {"lvl": 10, "task": "PURGE THE FILE 'LOGS_COPY.TXT'.", "valid": [r"^rm\s+logs_copy\.txt$"], "hint": "rm logs_copy.txt", "exp": "FILE DELETED."},
    {"lvl": 11, "task": "BROADCAST 'HELLO' TO THE CONSOLE.", "valid": [r"^echo\s+hello$"], "hint": "echo hello", "exp": "SIGNAL SENT."},
    {"lvl": 12, "task": "SEARCH 'SYS.LOG' FOR 'ERROR' STRINGS.", "valid": [r"^grep\s+error\s+sys\.log$"], "hint": "grep error sys.log", "exp": "VULNERABILITIES FOUND."},
    {"lvl": 13, "task": "DISPLAY THE HEAD (TOP) OF 'SYS.LOG'.", "valid": [r"^head\s+sys\.log$"], "hint": "head sys.log", "exp": "HEADER READ."},
    {"lvl": 14, "task": "DISPLAY THE LAST 5 LINES OF 'SYS.LOG'.", "valid": [r"^tail\s+-n\s+5\s+sys\.log$", r"^tail\s+-5\s+sys\.log$"], "hint": "tail -n 5 sys.log", "exp": "FOOTER READ."},
    {"lvl": 15, "task": "WIPE THE TERMINAL BUFFER.", "valid": [r"^clear$"], "hint": "clear", "exp": "BUFFER PURGED."},
    {"lvl": 16, "task": "ACCESS THE MANUAL FOR 'LS'.", "valid": [r"^man\s+ls$"], "hint": "man ls", "exp": "DOCUMENTATION ACCESSED."},
    {"lvl": 17, "task": "GRANT EXECUTION ACCESS TO 'SCRIPT.SH'.", "valid": [r"^chmod\s+\+x\s+script\.sh$"], "hint": "chmod +x script.sh", "exp": "PERMISSIONS OVERRIDDEN."},
    {"lvl": 18, "task": "PING EXTERNAL HOST 'GOOGLE.COM'.", "valid": [r"^ping\s+google\.com$"], "hint": "ping google.com", "exp": "PACKET EXCHANGED."},
    {"lvl": 19, "task": "IDENTIFY NETWORK INTERFACE DATA.", "valid": [r"^ifconfig$", r"^ip\s+addr$"], "hint": "ifconfig or ip addr", "exp": "NETWORK MAPPED."},
    {"lvl": 20, "task": "MONITOR RUNNING PROCESSES.", "valid": [r"^top$", r"^ps\s+aux$"], "hint": "top", "exp": "TASKS MONITORED."},
    {"lvl": 21, "task": "ZIP 'BACKUP/' INTO 'ARCHIVE.ZIP'.", "valid": [r"^zip\s+archive\.zip\s+backup$"], "effect": "📦 archive.zip", "hint": "zip [out] [dir]", "exp": "COMPRESSION COMPLETE."},
    {"lvl": 22, "task": "LOCATE ALL .TXT FILES IN LOCAL SCOPE.", "valid": [r"^find\s+\.\s+-name\s+\"\*\.txt\"$"], "hint": "find . -name \"*.txt\"", "exp": "FILES LOCATED."},
    {"lvl": 23, "task": "BOSS: ENUMERATE NODES AND COUNT OUTPUT LINES.", "valid": [r"^ls\s*\|\s*wc\s+-l$"], "hint": "ls | wc -l", "exp": "NODES QUANTIFIED."},
    {"lvl": 24, "task": "BOSS: FILTER 'SYS.LOG' FOR 'WARN' VIA PIPE.", "valid": [r"^cat\s+sys\.log\s*\|\s*grep\s+warn$"], "hint": "cat sys.log | grep warn", "exp": "WARNINGS ISOLATED."},
    {"lvl": 25, "task": "FINAL BOSS: EXTRACT ERRORS TO 'ERRORS.TXT'.", "valid": [r"^grep\s+error\s+sys\.log\s*>\s*errors\.txt$"], "effect": "📄 errors.txt", "hint": "grep error sys.log > errors.txt", "exp": "BREACH SUCCESSFUL."}
]

# --- 3. Session State ---
if 'lvl_idx' not in st.session_state: st.session_state.lvl_idx = 0
if 'fs' not in st.session_state: st.session_state.fs = ["📁 root/", "📄 .env", "📄 sys.log", "📄 script.sh"]
if 'health' not in st.session_state: st.session_state.health = 5
if 'success_phase' not in st.session_state: st.session_state.success_phase = False
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()

# --- 4. Main App ---
apply_hacker_styles()

with st.sidebar:
    st.markdown("### // SYSTEM_STATUS")
    st.metric("INTEGRITY", f"{st.session_state.health} HP")
    st.progress(st.session_state.lvl_idx / len(MISSIONS))
    st.write(f"NODE: {st.session_state.lvl_idx + 1} / {len(MISSIONS)}")
    st.divider()
    st.write("**// VIRTUAL_DRIVE**")
    for item in st.session_state.fs:
        st.caption(f"> {item}")
    if st.button("SYSTEM_WIPE"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.title("// TERMINAL_HERO //")

tab_play, tab_man = st.tabs(["[MISSION_CONTROL]", "[DECRYPT_MANUAL]"])

with tab_man:
    st.markdown("### // COMMAND_DECRYPTION_TABLE")
    st.code("NAV: ls, cd, pwd\nFILE: mkdir, touch, cp, mv, rm\nNET: ping, ifconfig\nPOWER: |, >, grep, wc, cat")

with tab_play:
    if st.session_state.health <= 0:
        st.error("// ACCESS_DENIED // SYSTEM_LOCKED")
        if st.button("HARD_REBOOT"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
    elif st.session_state.lvl_idx >= len(MISSIONS):
        st.balloons()
        st.header("// ROOT_ACCESS_GRANTED //")
        duration = round(time.time() - st.session_state.start_time, 2)
        st.success(f"Breach complete in {duration}s.")
        st.download_button("💾 DOWNLOAD_DECRYPT_KEY", "ROOT_CERT_1989", "access.txt")
    else:
        current = MISSIONS[st.session_state.lvl_idx]
        st.markdown(f'<div class="terminal-box">MISSION_{current["lvl"]}: {current["task"]}</div>', unsafe_allow_html=True)
        if st.button("REQUEST_HINT"):
            st.toast(f"// DECRYPTED: {current['hint']}")
        
        cmd = st.text_input("root@access:~$ ", key=f"q_{st.session_state.lvl_idx}").strip()

        if not st.session_state.success_phase:
            if st.button("EXECUTE_COMMAND"):
                if any(re.match(p, cmd.lower()) for p in current['valid']):
                    st.session_state.success_phase = True
                    if "effect" in current: st.session_state.fs.append(current['effect'])
                    st.rerun()
                else:
                    st.error("// COMMAND_ERROR //")
                    st.session_state.health -= 1
                    st.rerun()
        else:
            st.success(f"// {current['exp']}")
            if st.button("PROCEED_TO_NEXT_SECTOR ➡️"):
                st.session_state.lvl_idx += 1
                st.session_state.success_phase = False
                st.rerun()
