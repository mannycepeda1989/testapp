import streamlit as st
import re
import time

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
        .doc-section {
            background: rgba(0, 40, 0, 0.5);
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #00FF41;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. Mission Databases (60 Total) ---

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
    {"lvl": 23, "task": "Display current system date.", "valid": [r"^date$"], "hint": "date"},
    {"lvl": 24, "task": "Kill process with ID 1234.", "valid": [r"^kill\s+1234$"], "hint": "kill 1234"},
    {"lvl": 25, "task": "Sort 'list.txt' alphabetically.", "valid": [r"^sort\s+list\.txt$"], "hint": "sort list.txt"},
    {"lvl": 26, "task": "Count lines, words, and characters in 'config.tf'.", "valid": [r"^wc\s+config\.tf$"], "hint": "wc config.tf"},
    {"lvl": 27, "task": "Find 'config.tf' in the current directory subtree.", "valid": [r"^find\s+\.\s+-name\s+config\.tf$"], "hint": "find . -name config.tf"},
    {"lvl": 28, "task": "Search 'config.tf' for 'resource' and count occurrences.", "valid": [r"^grep\s+resource\s+config\.tf\s*\|\s*wc\s+-l$"], "hint": "grep ... | wc -l"},
    {"lvl": 29, "task": "Change file owner of 'scan.sh' to 'admin'.", "valid": [r"^chown\s+admin\s+scan\.sh$"], "hint": "chown admin scan.sh"},
    {"lvl": 30, "task": "Combine 'file1.txt' and 'file2.txt' into 'all.txt'.", "valid": [r"^cat\s+file1\.txt\s+file2\.txt\s*>\s*all\.txt$"], "hint": "cat f1 f2 > all"}
]

CHECKOV_MISSIONS = [
    {"lvl": 1, "task": "Scan the current directory.", "valid": [r"^checkov\s+-d\s+\.$"], "hint": "checkov -d ."},
    {"lvl": 2, "task": "Scan a specific file named 'main.tf'.", "valid": [r"^checkov\s+-f\s+main\.tf$"], "hint": "checkov -f main.tf"},
    {"lvl": 3, "task": "Output results in SARIF format.", "valid": [r"^checkov\s+-d\s+\.\s+-o\s+sarif$"], "hint": "-o sarif"},
    {"lvl": 4, "task": "Run only AWS-related checks.", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+aws$"], "hint": "--framework aws"},
    {"lvl": 5, "task": "Skip check 'CKV_AWS_1'.", "valid": [r"^checkov\s+-d\s+\.\s+--skip-check\s+ckv_aws_1$"], "hint": "--skip-check CKV_AWS_1"},
    {"lvl": 6, "task": "Enable soft-fail (exit 0).", "valid": [r"^checkov\s+-d\s+\.\s+--soft-fail$"], "hint": "--soft-fail"},
    {"lvl": 7, "task": "Run only check 'CKV_AWS_20'.", "valid": [r"^checkov\s+-d\s+\.\s+--check\s+ckv_aws_20$"], "hint": "--check CKV_AWS_20"},
    {"lvl": 8, "task": "Scan Kubernetes manifests.", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+kubernetes$"], "hint": "--framework kubernetes"},
    {"lvl": 9, "task": "Output to 'results.json'.", "valid": [r"^checkov\s+-d\s+\.\s+-o\s+json\s+>\s+results\.json$"], "hint": "-o json > results.json"},
    {"lvl": 10, "task": "Quiet mode (failures only).", "valid": [r"^checkov\s+-d\s+\.\s+--quiet$"], "hint": "--quiet"},
    {"lvl": 11, "task": "Scan CloudFormation template.", "valid": [r"^checkov\s+-f\s+template\.yaml\s+--framework\s+cloudformation$"], "hint": "--framework cloudformation"},
    {"lvl": 12, "task": "Download external modules.", "valid": [r"^checkov\s+--download-external-modules\s+true$"], "hint": "--download-external-modules true"},
    {"lvl": 13, "task": "Scan a Terraform plan JSON file.", "valid": [r"^checkov\s+-f\s+tfplan\.json$"], "hint": "-f tfplan.json"},
    {"lvl": 14, "task": "Include only 'High' and 'Critical' severity.", "valid": [r"^checkov\s+-d\s+\.\s+--check\s+high,critical$"], "hint": "--check high,critical"},
    {"lvl": 15, "task": "Use external policies directory 'policies'.", "valid": [r"^checkov\s+-d\s+\.\s+--external-checks-dir\s+policies$"], "hint": "--external-checks-dir policies"},
    {"lvl": 16, "task": "Use config file '.checkov.yaml'.", "valid": [r"^checkov\s+--config-file\s+\.checkov\.yaml$"], "hint": "--config-file .checkov.yaml"},
    {"lvl": 17, "task": "Scan Dockerfiles.", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+dockerfile$"], "hint": "--framework dockerfile"},
    {"lvl": 18, "task": "Show version.", "valid": [r"^checkov\s+-v$", r"^checkov\s+--version$"], "hint": "checkov -v"},
    {"lvl": 19, "task": "List available checks.", "valid": [r"^checkov\s+-l$", r"^checkov\s+--list$"], "hint": "-l"},
    {"lvl": 20, "task": "Create a baseline file.", "valid": [r"^checkov\s+-d\s+\.\s+--create-baseline$"], "hint": "--create-baseline"},
    {"lvl": 21, "task": "Use '.checkov.baseline' file.", "valid": [r"^checkov\s+-d\s+\.\s+--baseline\s+\.checkov\.baseline$"], "hint": "--baseline .checkov.baseline"},
    {"lvl": 22, "task": "Include 'vars.tfvars' file.", "valid": [r"^checkov\s+-d\s+\.\s+--var-file\s+vars\.tfvars$"], "hint": "--var-file vars.tfvars"},
    {"lvl": 23, "task": "Output in JUnit XML format.", "valid": [r"^checkov\s+-d\s+\.\s+-o\s+junitxml$"], "hint": "-o junitxml"},
    {"lvl": 24, "task": "Skip path 'temp/'.", "valid": [r"^checkov\s+-d\s+\.\s+--skip-path\s+temp$"], "hint": "--skip-path temp"},
    {"lvl": 25, "task": "Run 'Medium' severity checks.", "valid": [r"^checkov\s+-d\s+\.\s+--check\s+medium$"], "hint": "--check medium"},
    {"lvl": 26, "task": "Enable secret scanning.", "valid": [r"^checkov\s+-d\s+\.\s+--enable-secret-scan$"], "hint": "--enable-secret-scan"},
    {"lvl": 27, "task": "Scan ARM templates.", "valid": [r"^checkov\s+-d\s+\.\s+--framework\s+arm$"], "hint": "--framework arm"},
    {"lvl": 28, "task": "Set Bridgecrew ID 'my-id'.", "valid": [r"^checkov\s+--bc-id\s+my-id$"], "hint": "--bc-id my-id"},
    {"lvl": 29, "task": "List checks for terraform only.", "valid": [r"^checkov\s+--list\s+--framework\s+terraform$"], "hint": "--list --framework terraform"},
    {"lvl": 30, "task": "Quiet, soft-fail, and output JSON.", "valid": [r"^checkov\s+-d\s+\.\s+--quiet\s+--soft-fail\s+-o\s+json$"], "hint": "-d . --quiet --soft-fail -o json"}
]

# --- 3. Session State ---
for key, val in {'linux_idx': 0, 'checkov_idx': 0, 'health': 5, 'fs': ["📁 root/"], 'success': False}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. Main UI ---
apply_hacker_styles()

with st.sidebar:
    st.title("SEC-OPS HERO")
    st.metric("INTEGRITY", f"{st.session_state.health} HP")
    st.write("**DRIVE MAP:**")
    for i in st.session_state.fs: st.caption(f"> {i}")
    if st.button("RESET DATA"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

tab_linux, tab_checkov, tab_ref = st.tabs(["📂 LINUX QUEST", "🛡️ CHECKOV QUEST", "📖 DOCUMENTATION"])

with tab_ref:
    st.header("Technical Manual")
    
    with st.expander("🐧 Linux Command Reference", expanded=True):
        st.markdown("""
        ### Navigation & Core
        * `ls`: List files. Use `-a` for hidden files.
        * `cd [dir]`: Move into directory. `cd ..` to move out.
        * `pwd`: Print full path of current location.
        * `mkdir [name]`: Create new folder.
        
        ### File Management
        * `touch [file]`: Create empty file.
        * `mv [old] [new]`: Rename or move files.
        * `cp [src] [dst]`: Duplicate a file.
        * `rm [file]`: Delete a file.
        * `chmod +x [file]`: Make a script executable.
        * `chown [user] [file]`: Change file owner.
        
        ### Processing & Search
        * `grep [pattern] [file]`: Search for text.
        * `sort [file]`: Alphabetize lines.
        * `wc [file]`: Count lines/words/chars.
        * `cat [f1] [f2] > [f3]`: Combine files into a new one.
        * `find . -name "[name]"`: Search directory tree.
        
        ### System Status
        * `df -h`: Show disk space (human readable).
        * `du -sh [dir]`: Show size of a folder.
        * `top`: Live process monitor.
        * `kill [pid]`: Terminate a process.
        * `ip addr`: View network interfaces.
        """)

    with st.expander("🛡️ Checkov (IaC) Reference", expanded=True):
        st.markdown("""
        ### Scanning Targets
        * `-d .`: Scan current directory.
        * `-f [file]`: Scan specific Terraform/K8s/Yaml file.
        * `--framework [type]`: Limit scan to `aws`, `kubernetes`, `terraform`, `dockerfile`, `arm`, or `cloudformation`.
        
        ### Output & Formatting
        * `-o [format]`: Choose output format: `cli`, `json`, `sarif`, `junitxml`.
        * `--quiet`: Suppress passing checks; show only failures.
        * `> results.json`: Redirect CLI output to a file.
        
        ### Logic & Control
        * `--soft-fail`: Return exit code 0 even if failed checks are found.
        * `--check [ID/Severity]`: Run only specific checks (e.g., `CKV_AWS_1` or `high,critical`).
        * `--skip-check [ID]`: Exclude specific rules.
        * `--skip-path [path]`: Ignore specific folders or files.
        
        ### Advanced Features
        * `--create-baseline`: Save current failures to a file to ignore them in future runs.
        * `--baseline [file]`: Use a previously saved baseline.
        * `--var-file [file]`: Evaluate variables from a `.tfvars` file.
        * `--enable-secret-scan`: Scan for API keys/passwords in code.
        * `--config-file [file]`: Load all flags from a `.yaml` config.
        """)

def play_level(missions, index_key):
    idx = st.session_state[index_key]
    if idx >= len(missions):
        st.success("SECTOR COMPLETE. EXCELLENT WORK.")
        return
    
    current = missions[idx]
    st.markdown(f'<div class="terminal-box"><b>LEVEL {idx + 1} / {len(missions)}:</b><br>{current["task"]}</div>', unsafe_allow_html=True)
    
    if st.button("GET HINT", key=f"hint_{index_key}_{idx}"): 
        st.toast(f"HINT: {current['hint']}")
    
    cmd = st.text_input("user@terminal:~$ ", key=f"in_{index_key}_{idx}").strip()
    
    if not st.session_state.success:
        if st.button("RUN COMMAND", key=f"ex_{index_key}_{idx}"):
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
        if st.button("CONTINUE ➡️", key=f"nxt_{index_key}_{idx}"):
            st.session_state[index_key] += 1
            st.session_state.success = False
            st.rerun()

with tab_linux: play_level(LINUX_MISSIONS, 'linux_idx')
with tab_checkov: play_level(CHECKOV_MISSIONS, 'checkov_idx')
