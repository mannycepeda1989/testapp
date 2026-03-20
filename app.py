import streamlit as st
import re
import time

# --- 1. Terminal Aesthetic CSS ---
def apply_hacker_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
        @keyframes matrix-scroll { 0% { background-position: 0% 0%; } 100% { background-position: 0% 1000px; } }
        .stApp { background-image: linear-gradient(rgba(0, 255, 65, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 65, 0.05) 1px, transparent 1px); background-size: 100% 50px, 50px 100%; animation: matrix-scroll 60s linear infinite; }
        .terminal-box { border: 1px solid #00FF41; padding: 20px; background: rgba(0, 20, 0, 0.9); box-shadow: 0 0 15px #00FF41; margin-bottom: 25px; }
        .stTextInput input { background-color: #000 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 60-Mission Database ---

LINUX_MISSIONS = [
    {"lvl": 1, "task": "List files in the current directory.", "valid": [r"^ls$"], "hint": "ls"},
    {"lvl": 2, "task": "List all files, including hidden ones.", "valid": [r"^ls\s+-a$"], "hint": "ls -a"},
    {"lvl": 3, "task": "Create a directory named 'infra'.", "valid": [r"^mkdir\s+infra$"], "effect": "📁 infra/", "hint": "mkdir infra"},
    {"lvl": 4, "task": "Change directory into 'infra'.", "valid": [r"^cd\s+infra$"], "hint": "cd infra"},
    {"lvl": 5, "task": "Show the current working directory path.", "valid": [r"^pwd$"], "hint": "pwd"},
    {"lvl": 6, "task": "Go back to the parent directory.", "valid": [r"^cd\s+\.\.$"], "hint": "cd .."},
    {"lvl": 7, "task": "Create a file named 'main.tf'.", "valid": [r"^touch\s+main\.tf$"], "effect": "📄 main.tf", "hint": "touch main.tf"},
    {"lvl": 8, "task": "Rename 'main.tf' to 'config.tf'.", "valid": [r"^mv\s+main\.tf\s+config\.tf$"], "effect": "📄 config.tf", "hint": "mv main.tf config.tf"},
    {"lvl": 9, "task": "Copy 'config.tf' to 'backup.tf'.", "valid": [r"^cp\s+config\.tf\s+backup\.tf$"], "effect": "📄 backup.tf", "hint": "cp config.tf backup.tf"},
    {"lvl": 10, "task": "Delete 'backup.tf'.", "valid": [r"^rm\s+backup\.tf$"], "hint": "rm backup.tf"},
    {"lvl": 11, "task": "Print 'Ready' to the terminal.", "valid": [r"^echo\s+ready$"], "hint": "echo ready"},
    {"lvl": 12, "task": "Search for 'resource' in 'config.tf'.", "valid": [r"^grep\s+resource\s+config\.tf$"], "hint": "grep resource config.tf"},
    {"lvl": 13, "task": "View the top 10 lines of 'config.tf'.", "valid": [r"^head\s+config\.tf$"], "hint": "head config.tf"},
    {"lvl": 14, "task": "View the last 5 lines of 'config.tf'.", "valid": [r"^tail\s+-n\s+5\s+config\.tf$"], "hint": "tail -n 5 config.tf"},
    {"lvl": 15, "task": "Clear terminal output.", "valid": [r"^clear$"], "hint": "clear"},
    {"lvl": 16, "task": "Open manual for 'chmod'.", "valid": [r"^man\s+chmod$"], "hint": "man chmod"},
    {"lvl": 17, "task": "Make 'scan.sh' executable.", "valid": [r"^chmod\s+\+x\s+scan\.sh$"], "hint": "chmod +x scan.sh"},
    {"lvl": 18, "task": "Ping '8.8.8.8' once.", "valid": [r"^ping\s+-c\s+1\s+8\.8\.8\.8$"], "hint": "ping -c 1 8.8.8.8"},
    {"lvl": 19, "task": "Show network IP addresses.", "valid": [r"^ip\s+addr$", r"^ifconfig$"], "hint": "ip addr"},
    {"lvl": 20, "task": "Show active processes.", "valid": [r"^top$", r"^ps\s+aux$"], "hint": "top"},
    {"lvl": 21, "task": "Check disk space usage in human-readable format.", "valid": [r"^df\s+-h$"], "hint": "df -h"},
    {"lvl": 22, "task": "Check directory size of 'infra'.", "valid": [r"^du\s+-sh\s+infra$"], "hint": "du -sh infra"},
    {"lvl": 23, "task": "Display current system date and time.", "valid": [r"^date$"], "hint": "date"},
    {"lvl": 24, "task": "Kill process with ID 1234.", "valid": [r"^kill\s+1234$"], "hint": "kill 1234"},
    {"lvl": 25, "task": "Sort 'list.txt' alphabetically.", "valid": [r"^sort\s+list\.txt$"], "hint": "sort list.txt"},
    {"lvl": 26, "task": "Count lines, words, and characters in 'config.tf'.", "valid": [r"^wc\s+config\.tf$"], "hint": "wc config.tf"},
    {"lvl": 27, "task": "Find 'config.tf' in the current directory subtree.", "valid": [r"^find\s+\.\s+-name\s+config\.tf$"], "hint": "find . -name config.tf"},
    {"lvl": 28, "task": "Search 'config.tf' for 'resource' and count occurrences.", "valid": [r"^grep\s+resource\s+config\.tf\s*\|\s*wc\s+-l$"], "hint": "grep ... | wc -l"},
    {"lvl": 29, "task": "Change file owner of 'scan.sh' to 'admin'.", "valid": [r"^chown\s+admin\s+scan\.sh$"], "hint": "chown admin scan.sh"},
    {"lvl": 30, "task": "Combine 'file1.txt' and 'file2.txt' into 'all.txt'.", "valid": [r"^cat\s+file1\.txt\s+file2\.txt\s*>\s*all\.txt$"], "hint": "cat f1 f2 > all"}
]

CHECKOV_MISSIONS = [
    {"lvl": 1, "task": "Run Checkov to scan the current directory.", "valid": [r"^checkov\s+-d\s+\.$"], "hint": "checkov -d ."},
    {"lvl": 2, "task": "Scan a specific file named 'main.tf'.", "valid": [r"^checkov\s+-f\s+main\.tf$"], "hint": "checkov -f main.tf"},
    {"lvl": 3, "task": "Set Checkov output format to SARIF.", "valid": [r"^checkov\s+-d\s+\.\s+-o\s+sarif$"], "hint": "-o sarif"},
    {"lvl": 4, "task": "Run only AWS-related checks.", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+aws$"], "hint": "--framework aws"},
    {"lvl": 5, "task": "Skip a specific check (e.g., CKV_AWS_1).", "valid": [r"^checkov\s+-d\s+\.\s+--skip-check\s+ckv_aws_1$"], "hint": "--skip-check CKV_AWS_1"},
    {"lvl": 6, "task": "Enable soft-fail (exit code 0 even on failure).", "valid": [r"^checkov\s+-d\s+\.\s+--soft-fail$"], "hint": "--soft-fail"},
    {"lvl": 7, "task": "Run only a specific check (e.g., CKV_AWS_20).", "valid": [r"^checkov\s+-d\s+\.\s+--check\s+ckv_aws_20$"], "hint": "--check CKV_AWS_20"},
    {"lvl": 8, "task": "Scan Kubernetes manifest files.", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+kubernetes$"], "hint": "--framework kubernetes"},
    {"lvl": 9, "task": "Output results to a file named 'results.json'.", "valid": [r"^checkov\s+-d\s+\.\s+-o\s+json\s+>\s+results\.json$"], "hint": "-o json > results.json"},
    {"lvl": 10, "task": "Quiet mode (output only failed checks).", "valid": [r"^checkov\s+-d\s+\.\s+--quiet$"], "hint": "--quiet"},
    {"lvl": 11, "task": "Scan a CloudFormation template.", "valid": [r"^checkov\s+-f\s+template\.yaml\s+--framework\s+cloudformation$"], "hint": "--framework cloudformation"},
    {"lvl": 12, "task": "Download Checkov internal policies.", "valid": [r"^checkov\s+--download-external-modules\s+true$"], "hint": "--download-external-modules true"},
    {"lvl": 13, "task": "Evaluate a Terraform plan in JSON format.", "valid": [r"^checkov\s+-f\s+tfplan\.json$"], "hint": "-f tfplan.json"},
    {"lvl": 14, "task": "Include only 'High' and 'Critical' severity.", "valid": [r"^checkov\s+-d\s+\.\s+--check\s+high,critical$"], "hint": "--check high,critical"},
    {"lvl": 15, "task": "Use an external policies directory.", "valid": [r"^checkov\s+-d\s+\.\s+--external-checks-dir\s+policies$"], "hint": "--external-checks-dir policies"},
    {"lvl": 16, "task": "Run Checkov using a specific config file.", "valid": [r"^checkov\s+--config-file\s+\.checkov\.yaml$"], "hint": "--config-file .checkov.yaml"},
    {"lvl": 17, "task": "Scan Dockerfiles specifically.", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+dockerfile$"], "hint": "--framework dockerfile"},
    {"lvl": 18, "task": "Show current Checkov version.", "valid": [r"^checkov\s+-v$", r"^checkov\s+--version$"], "hint": "checkov -v"},
    {"lvl": 19, "task": "List all available checks.", "valid": [r"^checkov\s+-l$", r"^checkov\s+--list$"], "hint": "-l"},
    {"lvl": 20, "task": "Run Checkov and save a baseline file.", "valid": [r"^checkov\s+-d\s+\.\s+--create-baseline$"], "hint": "--create-baseline"},
    {"lvl": 21, "task": "Scan using a pre-existing baseline file.", "valid": [r"^checkov\s+-d\s+\.\s+--baseline\s+\.checkov\.baseline$"], "hint": "--baseline .checkov.baseline"},
    {"lvl": 22, "task": "Evaluate variable files during scan.", "valid": [r"^checkov\s+-d\s+\.\s+--var-file\s+vars\.tfvars$"], "hint": "--var-file vars.tfvars"},
    {"lvl": 3, "task": "Run scan and output in JUnit XML format.", "valid": [r"^checkov\s+-d\s+\.\s+-o\s+junitxml$"], "hint": "-o junitxml"},
    {"lvl": 24, "task": "Exclude specific directory 'temp/' from scan.", "valid": [r"^checkov\s+-d\s+\.\s+--skip-path\s+temp$"], "hint": "--skip-path temp"},
    {"lvl": 25, "task": "Run only 'Medium' severity checks.", "valid": [r"^checkov\s+-d\s+\.\s+--check\s+medium$"], "hint": "--check medium"},
    {"lvl": 26, "task": "Enable scanning of secrets.", "valid": [r"^checkov\s+-d\s+\.\s+--enable-secret-scan$"], "hint": "--enable-secret-scan"},
    {"lvl": 27, "task": "Scan ARM templates (Azure).", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+arm$"], "hint": "--framework arm"},
    {"lvl": 28, "task": "Set a specific API key for Bridgecrew integration.", "valid": [r"^checkov\s+--bc-id\s+.*$"], "hint": "--bc-id [key]"},
    {"lvl": 29, "task": "List checks filtered by framework 'terraform'.", "valid": [r"^checkov\s+--list\s+--framework\s+terraform$"], "hint": "--list --framework terraform"},
    {"lvl": 30, "task": "Final Boss: Scan directory, quiet mode, soft-fail, and output JSON.", "valid": [r"^checkov\s+-d\s+\.\s+--quiet\s+--soft-fail\s+-o\s+json$"], "hint": "-d . --quiet --soft-fail -o json"}
]

# --- 3. Session State ---
for key, val in {'linux_idx': 0, 'checkov_idx': 0, 'health': 5, 'fs': ["📁 root/"], 'success': False}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. UI ---
apply_hacker_styles()

with st.sidebar:
    st.title("SEC-OPS TRAINER")
    st.metric("INTEGRITY", f"{st.session_state.health} HP")
    st.write("**DRIVE MAP:**")
    for i in st.session_state.fs: st.caption(f"> {i}")
    if st.button("RESET PROGRESS"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

tab_linux, tab_checkov, tab_ref = st.tabs(["📂 LINUX QUEST", "🛡️ CHECKOV QUEST", "📖 DOCUMENTATION"])

with tab_ref:
    st.header("Comprehensive Command Dictionary")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🐧 Linux Ops")
        st.code("ls, ls -a, pwd, cd, cd .., mkdir, touch, mv, cp, rm, echo, clear, man, chmod +x")
        st.code("df -h, du -sh, date, kill [id], sort, wc, find . -name, chown, cat f1 f2 > f3")
    with c2:
        st.subheader("🛡️ Checkov CLI")
        st.code("-d, -f, -o (json, sarif, junitxml), --framework (aws, kubernetes, terraform, arm, dockerfile)")
        st.code("--check (high, medium, ID), --skip-check, --soft-fail, --quiet, --create-baseline, --baseline, --var-file, --enable-secret-scan")

def play_level(missions, index_key):
    idx = st.session_state[index_key]
    if idx >= len(missions):
        st.success("SECTOR SECURED. CONGRATULATIONS.")
        return
    current = missions[idx]
    st.markdown(f'<div class="terminal-box"><b>MISSION {idx + 1} / {len(missions)}:</b><br>{current["task"]}</div>', unsafe_allow_html=True)
    if st.button("HINT", key=f"hint_{index_key}_{idx}"): st.toast(f"HINT: {current['hint']}")
    cmd = st.text_input("user@terminal:~$ ", key=f"in_{index_key}_{idx}").strip()
    if not st.session_state.success:
        if st.button("EXECUTE", key=f"ex_{index_key}_{idx}"):
            if any(re.match(p, cmd.lower()) for p in current['valid']):
                st.session_state.success = True
                if "effect" in current: st.session_state.fs.append(current['effect'])
                st.rerun()
            else:
                st.error("SYNTAX ERROR")
                st.session_state.health -= 1
                st.rerun()
    else:
        st.success("COMMAND ACCEPTED")
        if st.button("NEXT LEVEL ➡️", key=f"nxt_{index_key}_{idx}"):
            st.session_state[index_key] += 1
            st.session_state.success = False
            st.rerun()

with tab_linux: play_level(LINUX_MISSIONS, 'linux_idx')
with tab_checkov: play_level(CHECKOV_MISSIONS, 'checkov_idx')
