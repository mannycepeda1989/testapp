import streamlit as st
import re

# --- 1. Terminal Aesthetic CSS ---
def apply_hacker_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
        .terminal-box { border: 1px solid #00FF41; padding: 20px; background: rgba(0, 20, 0, 0.9); box-shadow: 0 0 15px #00FF41; margin-bottom: 25px; }
        .stTextInput input { background-color: #000 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; }
        .error-hint { color: #FF3131; font-weight: bold; border: 1px solid #FF3131; padding: 10px; margin-top: 10px; background: rgba(50, 0, 0, 0.9); }
        .lockdown { color: #FF0000; font-size: 30px; text-align: center; border: 5px solid #FF0000; padding: 50px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. Mission Databases (Linux & Checkov) ---
# (Databases remain identical to previous verified versions to ensure logical consistency)
LINUX_MISSIONS = [
    {"lvl": 1, "task": "List files in the current directory.", "valid": [r"^ls$"], "hint": "ls"},
    {"lvl": 2, "task": "List all files, including hidden ones.", "valid": [r"^ls\s+-a$"], "hint": "ls -a"},
    {"lvl": 3, "task": "Create a directory named 'infra'.", "valid": [r"^mkdir\s+infra$"], "hint": "mkdir infra"},
    {"lvl": 4, "task": "Change directory into 'infra'.", "valid": [r"^cd\s+infra$"], "hint": "cd infra"},
    {"lvl": 5, "task": "Show the current working directory path.", "valid": [r"^pwd$"], "hint": "pwd"},
    {"lvl": 6, "task": "Go back to the parent directory.", "valid": [r"^cd\s+\.\.$"], "hint": "cd .."},
    {"lvl": 7, "task": "Create a file named 'main.tf'.", "valid": [r"^touch\s+main\.tf$"], "hint": "touch main.tf"},
    {"lvl": 8, "task": "Rename 'main.tf' to 'config.tf'.", "valid": [r"^mv\s+main\.tf\s+config\.tf$"], "hint": "mv main.tf config.tf"},
    {"lvl": 9, "task": "Copy 'config.tf' to 'backup.tf'.", "valid": [r"^cp\s+config\.tf\s+backup\.tf$"], "hint": "cp config.tf backup.tf"},
    {"lvl": 10, "task": "Delete 'backup.tf'.", "valid": [r"^rm\s+backup\.tf$"], "hint": "rm backup.tf"},
    {"lvl": 11, "task": "Print 'Ready' to the terminal.", "valid": [r"^echo\s+ready$"], "hint": "echo ready"},
    {"lvl": 12, "task": "Search for 'resource' in 'config.tf'.", "valid": [r"^grep\s+resource\s+config\.tf$"], "hint": "grep resource config.tf"},
    {"lvl": 13, "task": "View the top of 'config.tf'.", "valid": [r"^head\s+config\.tf$"], "hint": "head config.tf"},
    {"lvl": 14, "task": "View the last 5 lines of 'config.tf'.", "valid": [r"^tail\s+-n\s+5\s+config\.tf$"], "hint": "tail -n 5 config.tf"},
    {"lvl": 15, "task": "Clear terminal output.", "valid": [r"^clear$"], "hint": "clear"},
    {"lvl": 16, "task": "Open manual for 'chmod'.", "valid": [r"^man\s+chmod$"], "hint": "man chmod"},
    {"lvl": 17, "task": "Make 'scan.sh' executable.", "valid": [r"^chmod\s+\+x\s+scan\.sh$"], "hint": "chmod +x scan.sh"},
    {"lvl": 18, "task": "Ping '8.8.8.8' once.", "valid": [r"^ping\s+-c\s+1\s+8\.8\.8\.8$"], "hint": "ping -c 1 8.8.8.8"},
    {"lvl": 19, "task": "Show network IP addresses.", "valid": [r"^ip\s+addr$"], "hint": "ip addr"},
    {"lvl": 20, "task": "Show active processes.", "valid": [r"^ps\s+aux$", r"^top$"], "hint": "ps aux"},
    {"lvl": 21, "task": "Check disk space usage.", "valid": [r"^df\s+-h$"], "hint": "df -h"},
    {"lvl": 22, "task": "Check size of 'infra' directory.", "valid": [r"^du\s+-sh\s+infra$"], "hint": "du -sh infra"},
    {"lvl": 23, "task": "Display system date.", "valid": [r"^date$"], "hint": "date"},
    {"lvl": 24, "task": "Kill process ID 1234.", "valid": [r"^kill\s+1234$"], "hint": "kill 1234"},
    {"lvl": 25, "task": "Sort 'list.txt'.", "valid": [r"^sort\s+list\.txt$"], "hint": "sort list.txt"},
    {"lvl": 26, "task": "Count lines in 'config.tf'.", "valid": [r"^wc\s+-l\s+config\.tf$"], "hint": "wc -l config.tf"},
    {"lvl": 27, "task": "Find 'config.tf' in current tree.", "valid": [r"^find\s+\.\s+-name\s+config\.tf$"], "hint": "find . -name config.tf"},
    {"lvl": 28, "task": "Combine file redirection.", "valid": [r"^cat\s+f1\s+f2\s*>\s*all\.txt$"], "hint": "cat f1 f2 > all.txt"},
    {"lvl": 29, "task": "Change owner to 'admin'.", "valid": [r"^chown\s+admin\s+scan\.sh$"], "hint": "chown admin scan.sh"},
    {"lvl": 30, "task": "Final boss: grep and wc pipe.", "valid": [r"^grep\s+resource\s+config\.tf\s*\|\s*wc\s+-l$"], "hint": "grep resource config.tf | wc -l"}
]

CHECKOV_MISSIONS = [
    {"lvl": 1, "task": "Scan the current directory (shorthand).", "valid": [r".*-d\s+\..*"], "hint": "-d ."},
    {"lvl": 2, "task": "Scan 'main.tf' (shorthand).", "valid": [r".*-f\s+main\.tf.*"], "hint": "-f main.tf"},
    {"lvl": 3, "task": "Run all checks 'HIGH' and above (threshold).", "valid": [r".*--check\s+high.*"], "hint": "Checkov is inclusive. Use --check HIGH."},
    {"lvl": 4, "task": "Skip all checks 'MEDIUM' and below (threshold).", "valid": [r".*--skip-check\s+medium.*"], "hint": "Use --skip-check MEDIUM."},
    {"lvl": 5, "task": "Run only check ID: CKV_AWS_20.", "valid": [r".*--check\s+ckv_aws_20.*"], "hint": "--check CKV_AWS_20"},
    {"lvl": 6, "task": "Limit scan to 'kubernetes' framework.", "valid": [r".*--framework\s+kubernetes.*"], "hint": "--framework kubernetes"},
    {"lvl": 7, "task": "Output in 'sarif' format.", "valid": [r".*-o\s+sarif.*"], "hint": "-o sarif"},
    {"lvl": 8, "task": "Enable compact output.", "valid": [r".*--compact.*"], "hint": "--compact"},
    {"lvl": 9, "task": "Quiet mode (failures only).", "valid": [r".*--quiet.*"], "hint": "--quiet"},
    {"lvl": 10, "task": "Show current configuration.", "valid": [r".*--show-config.*"], "hint": "--show-config"},
    {"lvl": 11, "task": "Enable global soft-fail.", "valid": [r".*--soft-fail(?!\-on).*"], "hint": "--soft-fail"},
    {"lvl": 12, "task": "Hard-fail ONLY on 'CRITICAL' findings.", "valid": [r".*--hard-fail-on\s+critical.*"], "hint": "--hard-fail-on CRITICAL"},
    {"lvl": 13, "task": "Soft-fail ONLY on 'LOW' findings.", "valid": [r".*--soft-fail-on\s+low.*"], "hint": "--soft-fail-on LOW"},
    {"lvl": 14, "task": "Scan for secrets.", "valid": [r".*--enable-secret-scan.*"], "hint": "--enable-secret-scan"},
    {"lvl": 15, "task": "Use external checks directory 'custom'.", "valid": [r".*--external-checks-dir\s+custom.*"], "hint": "--external-checks-dir custom"},
    {"lvl": 16, "task": "Download external modules.", "valid": [r".*--download-external-modules\s+true.*"], "hint": "--download-external-modules true"},
    {"lvl": 17, "task": "Create a new baseline file.", "valid": [r".*--create-baseline.*"], "hint": "--create-baseline"},
    {"lvl": 18, "task": "Use existing baseline '.checkov.baseline'.", "valid": [r".*--baseline\s+\.checkov\.baseline.*"], "hint": "--baseline .checkov.baseline"},
    {"lvl": 19, "task": "Use config file 'scan-policy.yaml'.", "valid": [r".*--config-file\s+scan-policy\.yaml.*"], "hint": "--config-file scan-policy.yaml"},
    {"lvl": 20, "task": "Load vars from 'prod.tfvars'.", "valid": [r".*--var-file\s+prod\.tfvars.*"], "hint": "--var-file prod.tfvars"},
    {"lvl": 21, "task": "Enable deep analysis.", "valid": [r".*--deep-analysis.*"], "hint": "--deep-analysis"},
    {"lvl": 22, "task": "Set repo root to '/app'.", "valid": [r".*--repo-root-for-plan-enrichment\s+/app.*"], "hint": "--repo-root-for-plan-enrichment /app"},
    {"lvl": 23, "task": "Skip path 'vendor/'.", "valid": [r".*--skip-path\s+vendor.*"], "hint": "--skip-path vendor"},
    {"lvl": 24, "task": "Skip 'dockerfile' framework.", "valid": [r".*--skip-framework\s+dockerfile.*"], "hint": "--skip-framework dockerfile"},
    {"lvl": 25, "task": "List checks for 'arm' framework.", "valid": [r".*--list.*--framework\s+arm.*"], "hint": "--list --framework arm"},
    {"lvl": 26, "task": "Set output path to './reports'.", "valid": [r".*--output-file-path\s+\./reports.*"], "hint": "--output-file-path ./reports"},
    {"lvl": 27, "task": "Set BC ID 'my-key'.", "valid": [r".*--bc-id\s+my-key.*"], "hint": "--bc-id my-key"},
    {"lvl": 28, "task": "Check version.", "valid": [r".*(-v|--version).*"], "hint": "-v"},
    {"lvl": 29, "task": "Output JSON and JUnit XML.", "valid": [r".*-o\s+(json,junitxml|junitxml,json).*"], "hint": "-o json,junitxml"},
    {"lvl": 30, "task": "FINAL BOSS: Quiet, Soft-Fail, JSON, Directory '.'", "valid": [r".*--quiet.*--soft-fail.*-o\s+json.*-d\s+\..*"], "hint": "--quiet --soft-fail -o json -d ."}
]

# --- 3. Session State Logic ---
state_defaults = {
    'linux_idx': 0, 
    'checkov_idx': 0, 
    'score': 0,
    'strikes': 0, 
    'attempts_this_lvl': 0,
    'locked_down': False,
    'last_error': "", 
    'success': False
}
for key, val in state_defaults.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. UI Rendering ---
apply_hacker_styles()

with st.sidebar:
    st.title("SEC-OPS HERO")
    st.metric("TOTAL SCORE", f"{st.session_state.score} PTS")
    st.write(f"CURRENT STRIKES: {'🔴' * st.session_state.strikes}{'⚪' * (3 - st.session_state.strikes)}")
    
    if st.button("RELOAD SYSTEM (RESET)"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

if st.session_state.locked_down:
    st.markdown('<div class="lockdown">🚨 SYSTEM LOCKDOWN 🚨<br>Too many failed attempts. Security breach suspected.</div>', unsafe_allow_html=True)
    if st.button("REAUTHENTICATE (RESTART)"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.stop()

tab_linux, tab_checkov, tab_ref = st.tabs(["📂 LINUX QUEST", "🛡️ CHECKOV FLAGS", "📖 REFERENCE"])

with tab_ref:
    st.header("Checkov Parameter Reference")
    st.markdown("""
    ### 🎯 Threshold Logic
    - `HIGH`: Includes High & Critical.
    - `MEDIUM`: Includes Medium, High, Critical.
    - `LOW`: Includes everything.
    
    ### 🛠️ Key Flags
    - `--check`: Include only.
    - `--skip-check`: Exclude.
    - `--soft-fail`: Exit 0 global.
    - `--soft-fail-on`: Exit 0 specific.
    - `--hard-fail-on`: Force Exit 1.
    """)

def play_level(missions, index_key):
    idx = st.session_state[index_key]
    if idx >= len(missions):
        st.success("SECTOR SECURED. ACCESS LEVEL: ELITE.")
        return
    
    current = missions[idx]
    st.markdown(f'<div class="terminal-box"><b>MISSION {idx + 1}:</b><br>{current["task"]}</div>', unsafe_allow_html=True)
    
    # UI Control Row: Input and Hint
    col_input, col_hint = st.columns([4, 1])
    with col_hint:
        if st.button("GET HINT", key=f"hint_btn_{index_key}_{idx}"):
            st.info(f"HINT: {current['hint']}")

    cmd = col_input.text_input("user@terminal:~$ ", key=f"in_{index_key}_{idx}").strip()
    
    if st.session_state.last_error:
        st.markdown(f'<div class="error-hint">⚠️ SYNTAX ERROR: {st.session_state.last_error}</div>', unsafe_allow_html=True)

    if not st.session_state.success:
        if st.button("EXECUTE", key=f"ex_{index_key}_{idx}"):
            if any(re.search(p, cmd.lower()) for p in current['valid']):
                # Scoring Logic
                if st.session_state.attempts_this_lvl == 0: st.session_state.score += 100
                elif st.session_state.attempts_this_lvl == 1: st.session_state.score += 50
                else: st.session_state.score += 25
                
                st.session_state.success = True
                st.session_state.last_error = ""
                st.session_state.strikes = 0 # Reset strikes on success
                st.rerun()
            else:
                st.session_state.attempts_this_lvl += 1
                st.session_state.strikes += 1
                st.session_state.last_error = f"Invalid Command. Strike {st.session_state.strikes}/3"
                
                if st.session_state.strikes >= 3:
                    st.session_state.locked_down = True
                st.rerun()
    else:
        st.success(f"ACCESS GRANTED. +{100 if st.session_state.attempts_this_lvl == 0 else 50 if st.session_state.attempts_this_lvl == 1 else 25} PTS")
        if st.button("CONTINUE ➡️", key=f"nxt_{index_key}_{idx}"):
            st.session_state[index_key] += 1
            st.session_state.success = False
            st.session_state.last_error = ""
            st.session_state.attempts_this_lvl = 0
            st.rerun()

with tab_linux: play_level(LINUX_MISSIONS, 'linux_idx')
with tab_checkov: play_level(CHECKOV_MISSIONS, 'checkov_idx')
