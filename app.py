import streamlit as st
import re

# --- 1. Terminal Aesthetic CSS ---
def apply_hacker_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
        .terminal-box { border: 1px solid #00FF41; padding: 20px; background: rgba(0, 20, 0, 0.9); box-shadow: 0 0 15px #00FF41; margin-bottom: 25px; }
        .stTextInput input { background-color: #000 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; }
        /* Error feedback styling */
        .error-hint { color: #FF3131; font-weight: bold; border: 1px solid #FF3131; padding: 10px; margin-top: 10px; background: rgba(50, 0, 0, 0.9); }
        </style>
    """, unsafe_allow_html=True)

# --- 2. Mission Databases ---

LINUX_MISSIONS = [
    {"lvl": 1, "task": "List files in the current directory.", "valid": [r"^ls$"], "hint": "Use 'ls'"},
    {"lvl": 2, "task": "List all files, including hidden ones.", "valid": [r"^ls\s+-a$"], "hint": "Use 'ls -a'"},
    {"lvl": 3, "task": "Create a directory named 'infra'.", "valid": [r"^mkdir\s+infra$"], "hint": "Use 'mkdir infra'"},
    {"lvl": 4, "task": "Change directory into 'infra'.", "valid": [r"^cd\s+infra$"], "hint": "Use 'cd infra'"},
    {"lvl": 5, "task": "Show the current working directory path.", "valid": [r"^pwd$"], "hint": "Use 'pwd'"},
    {"lvl": 6, "task": "Go back to the parent directory.", "valid": [r"^cd\s+\.\.$"], "hint": "Use 'cd ..'"},
    {"lvl": 7, "task": "Create a file named 'main.tf'.", "valid": [r"^touch\s+main\.tf$"], "hint": "Use 'touch'"},
    {"lvl": 8, "task": "Rename 'main.tf' to 'config.tf'.", "valid": [r"^mv\s+main\.tf\s+config\.tf$"], "hint": "Use 'mv [old] [new]'"},
    {"lvl": 9, "task": "Copy 'config.tf' to 'backup.tf'.", "valid": [r"^cp\s+config\.tf\s+backup\.tf$"], "hint": "Use 'cp [src] [dst]'"},
    {"lvl": 10, "task": "Delete 'backup.tf'.", "valid": [r"^rm\s+backup\.tf$"], "hint": "Use 'rm'"},
    {"lvl": 11, "task": "Print 'Ready' to the terminal.", "valid": [r"^echo\s+ready$"], "hint": "Use 'echo'"},
    {"lvl": 12, "task": "Search for 'resource' in 'config.tf'.", "valid": [r"^grep\s+resource\s+config\.tf$"], "hint": "Use 'grep'"},
    {"lvl": 13, "task": "View the top of 'config.tf'.", "valid": [r"^head\s+config\.tf$"], "hint": "Use 'head'"},
    {"lvl": 14, "task": "View the last 5 lines of 'config.tf'.", "valid": [r"^tail\s+-n\s+5\s+config\.tf$"], "hint": "Use 'tail -n 5'"},
    {"lvl": 15, "task": "Clear terminal output.", "valid": [r"^clear$"], "hint": "Use 'clear'"},
    {"lvl": 16, "task": "Open manual for 'chmod'.", "valid": [r"^man\s+chmod$"], "hint": "Use 'man'"},
    {"lvl": 17, "task": "Make 'scan.sh' executable.", "valid": [r"^chmod\s+\+x\s+scan\.sh$"], "hint": "Use 'chmod +x'"},
    {"lvl": 18, "task": "Ping '8.8.8.8' once.", "valid": [r"^ping\s+-c\s+1\s+8\.8\.8\.8$"], "hint": "Use 'ping -c 1'"},
    {"lvl": 19, "task": "Show network IP addresses.", "valid": [r"^ip\s+addr$"], "hint": "Use 'ip addr'"},
    {"lvl": 20, "task": "Show active processes.", "valid": [r"^ps\s+aux$", r"^top$"], "hint": "Use 'ps aux' or 'top'"},
    {"lvl": 21, "task": "Check disk space usage.", "valid": [r"^df\s+-h$"], "hint": "Use 'df -h'"},
    {"lvl": 22, "task": "Check size of 'infra' directory.", "valid": [r"^du\s+-sh\s+infra$"], "hint": "Use 'du -sh'"},
    {"lvl": 23, "task": "Display system date.", "valid": [r"^date$"], "hint": "Use 'date'"},
    {"lvl": 24, "task": "Kill process ID 1234.", "valid": [r"^kill\s+1234$"], "hint": "Use 'kill'"},
    {"lvl": 25, "task": "Sort 'list.txt'.", "valid": [r"^sort\s+list\.txt$"], "hint": "Use 'sort'"},
    {"lvl": 26, "task": "Count lines in 'config.tf'.", "valid": [r"^wc\s+-l\s+config\.tf$"], "hint": "Use 'wc -l'"},
    {"lvl": 27, "task": "Find 'config.tf' in current tree.", "valid": [r"^find\s+\.\s+-name\s+config\.tf$"], "hint": "Use 'find'"},
    {"lvl": 28, "task": "Combine file redirection.", "valid": [r"^cat\s+f1\s+f2\s*>\s*all\.txt$"], "hint": "Use '>' to redirect"},
    {"lvl": 29, "task": "Change owner to 'admin'.", "valid": [r"^chown\s+admin\s+scan\.sh$"], "hint": "Use 'chown'"},
    {"lvl": 30, "task": "Final boss: grep and wc pipe.", "valid": [r"^grep\s+resource\s+config\.tf\s*\|\s*wc\s+-l$"], "hint": "Use '|' to pipe"}
]

CHECKOV_MISSIONS = [
    # --- SCANNING TARGETS ---
    {"lvl": 1, "task": "Scan the current directory using the shorthand directory flag.", "valid": [r".*-d\s+\..*"], "hint": "The flag is -d followed by the path '.'"},
    {"lvl": 2, "task": "Scan a specific file named 'main.tf' using the shorthand file flag.", "valid": [r".*-f\s+main\.tf.*"], "hint": "The flag is -f"},
    
    # --- FILTERING ---
    {"lvl": 3, "task": "Run only checks with 'HIGH' and 'CRITICAL' severity.", "valid": [r".*--check\s+(high,critical|critical,high).*"], "hint": "Use --check [SEVERITY]"},
    {"lvl": 4, "task": "Skip only checks with 'LOW' severity.", "valid": [r".*--skip-check\s+low.*"], "hint": "Use --skip-check [SEVERITY]"},
    {"lvl": 5, "task": "Run only a specific check ID: CKV_AWS_20.", "valid": [r".*--check\s+ckv_aws_20.*"], "hint": "Use --check [ID]"},
    {"lvl": 6, "task": "Limit the scan to only 'kubernetes' and 'terraform' frameworks.", "valid": [r".*--framework\s+(kubernetes,terraform|terraform,kubernetes).*"], "hint": "Use --framework [comma-separated list]"},

    # --- OUTPUT & DISPLAY ---
    {"lvl": 7, "task": "Output results in 'json' format.", "valid": [r".*-o\s+json.*"], "hint": "Use -o json"},
    {"lvl": 8, "task": "Enable 'compact' output to remove code blocks.", "valid": [r".*--compact.*"], "hint": "The flag is --compact"},
    {"lvl": 9, "task": "Only show failed checks in the terminal.", "valid": [r".*--quiet.*"], "hint": "The flag is --quiet"},
    {"lvl": 10, "task": "Show all configuration settings currently being used.", "valid": [r".*--show-config.*"], "hint": "The flag is --show-config"},
    
    # --- FAIL LOGIC ---
    {"lvl": 11, "task": "Ensure the exit code is 0 regardless of failures.", "valid": [r".*--soft-fail.*"], "hint": "The flag is --soft-fail"},
    {"lvl": 12, "task": "Hard-fail the scan ONLY if 'CRITICAL' issues are found.", "valid": [r".*--hard-fail-on\s+critical.*"], "hint": "Use --hard-fail-on [SEVERITY]"},
    {"lvl": 13, "task": "Soft-fail (exit 0) if the severity is 'LOW'.", "valid": [r".*--soft-fail-on\s+low.*"], "hint": "Use --soft-fail-on [SEVERITY]"},

    # --- ADVANCED & EXTERNAL ---
    {"lvl": 14, "task": "Enable secret scanning.", "valid": [r".*--enable-secret-scan.*"], "hint": "The flag is --enable-secret-scan"},
    {"lvl": 15, "task": "Use an external policies directory called 'my_rules'.", "valid": [r".*--external-checks-dir\s+my_rules.*"], "hint": "The flag is --external-checks-dir"},
    {"lvl": 16, "task": "Download external modules before scanning.", "valid": [r".*--download-external-modules\s+true.*"], "hint": "Use --download-external-modules true"},
    {"lvl": 17, "task": "Scan a directory and create a baseline file.", "valid": [r".*--create-baseline.*"], "hint": "The flag is --create-baseline"},
    {"lvl": 18, "task": "Run scan against an existing baseline file '.checkov.baseline'.", "valid": [r".*--baseline\s+\.checkov\.baseline.*"], "hint": "Use --baseline [FILENAME]"},
    {"lvl": 19, "task": "Load all CLI flags from a file called 'config.yaml'.", "valid": [r".*--config-file\s+config\.yaml.*"], "hint": "The flag is --config-file"},
    {"lvl": 20, "task": "Evaluate Terraform variables using 'dev.tfvars'.", "valid": [r".*--var-file\s+dev\.tfvars.*"], "hint": "Use --var-file [FILENAME]"},

    # --- ENRICHMENT & MISC ---
    {"lvl": 21, "task": "Enable deep analysis for plan enrichment.", "valid": [r".*--deep-analysis.*"], "hint": "The flag is --deep-analysis"},
    {"lvl": 22, "task": "Set the repo root for plan enrichment to '/src'.", "valid": [r".*--repo-root-for-plan-enrichment\s+/src.*"], "hint": "The flag is --repo-root-for-plan-enrichment"},
    {"lvl": 23, "task": "Skip a specific path called 'tests/'.", "valid": [r".*--skip-path\s+tests.*"], "hint": "Use --skip-path [PATH]"},
    {"lvl": 24, "task": "Skip the 'arm' framework entirely.", "valid": [r".*--skip-framework\s+arm.*"], "hint": "Use --skip-framework [FRAMEWORK]"},
    {"lvl": 25, "task": "List available checks for 'dockerfile' only.", "valid": [r".*--list.*--framework\s+dockerfile.*"], "hint": "Use --list and --framework"},
    {"lvl": 26, "task": "Output results to a specific directory path '/tmp/results'.", "valid": [r".*--output-file-path\s+/tmp/results.*"], "hint": "The flag is --output-file-path"},
    {"lvl": 27, "task": "Set a specific BC ID for platform integration.", "valid": [r".*--bc-id\s+.*"], "hint": "The flag is --bc-id"},
    {"lvl": 28, "task": "Show Checkov version.", "valid": [r".*(-v|--version).*"], "hint": "Use -v"},
    {"lvl": 29, "task": "Output results in both 'cli' and 'sarif' formats.", "valid": [r".*-o\s+(cli,sarif|sarif,cli).*"], "hint": "Use -o cli,sarif"},
    {"lvl": 30, "task": "FINAL BOSS: Quiet, Compact, Soft-Fail, and scan directory '.'.", "valid": [r".*--quiet.*--compact.*--soft-fail.*-d\s+\..*"], "hint": "Combine --quiet, --compact, --soft-fail, and -d ."}
]

# --- 3. Session State ---
for key, val in {'linux_idx': 0, 'checkov_idx': 0, 'health': 5, 'last_error': "", 'success': False}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. Main UI ---
apply_hacker_styles()

with st.sidebar:
    st.title("SEC-OPS HERO")
    st.metric("INTEGRITY", f"{st.session_state.health} HP")
    if st.button("RESET DATA"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

tab_linux, tab_checkov, tab_ref = st.tabs(["📂 LINUX QUEST", "🛡️ CHECKOV FLAGS", "📖 REFERENCE"])

with tab_ref:
    st.header("Checkov Parameter Reference")
    st.caption("Based on: checkov.io/2.Basics/CLI%20Command%20Reference.html")
    st.markdown("""
    ### 🎯 Scanning Targets
    - `-d, --directory`: Folder to scan.
    - `-f, --file`: File to scan.
    
    ### 🔍 Filtering & Suppression
    - `--check [ID/SEV]`: Run only these checks.
    - `--skip-check [ID/SEV]`: Exclude these checks.
    - `--framework [type]`: limit to terraform, kubernetes, dockerfile, arm, etc.
    - `--skip-path [path]`: Ignore specific folders.
    - `--skip-framework [type]`: Exclude specific engines.

    ### 🛠️ Execution Logic
    - `--soft-fail`: Exit with code 0 regardless.
    - `--soft-fail-on [ID/SEV]`: Only exit 0 for these specific items.
    - `--hard-fail-on [ID/SEV]`: Force exit code 1 for these specific items.
    
    ### 📊 Output & Analysis
    - `-o, --output`: formats (cli, json, sarif, junitxml).
    - `--quiet`: Failure output only.
    - `--compact`: No code snippets.
    - `--create-baseline`: Mark current errors as 'known'.
    - `--baseline [file]`: Use the baseline file.
    - `--enable-secret-scan`: Look for leaked keys.
    """)

def play_level(missions, index_key):
    idx = st.session_state[index_key]
    if idx >= len(missions):
        st.success("SECTOR COMPLETE.")
        return
    
    current = missions[idx]
    st.markdown(f'<div class="terminal-box"><b>MISSION {idx + 1}:</b><br>{current["task"]}</div>', unsafe_allow_html=True)
    
    # Immediate Feedback Logic
    if st.session_state.last_error:
        st.markdown(f'<div class="error-hint">⚠️ SYNTAX ERROR: {st.session_state.last_error}</div>', unsafe_allow_html=True)

    cmd = st.text_input("user@terminal:~$ ", key=f"in_{index_key}_{idx}").strip()
    
    if not st.session_state.success:
        if st.button("RUN COMMAND", key=f"ex_{index_key}_{idx}"):
            if any(re.search(p, cmd.lower()) for p in current['valid']):
                st.session_state.success = True
                st.session_state.last_error = "" # Clear errors on success
                st.rerun()
            else:
                st.session_state.health -= 1
                st.session_state.last_error = current['hint'] # Set the hint as the error message
                st.rerun()
    else:
        st.success("ACCESS GRANTED.")
        if st.button("CONTINUE ➡️", key=f"nxt_{index_key}_{idx}"):
            st.session_state[index_key] += 1
            st.session_state.success = False
            st.session_state.last_error = ""
            st.rerun()

with tab_linux: play_level(LINUX_MISSIONS, 'linux_idx')
with tab_checkov: play_level(CHECKOV_MISSIONS, 'checkov_idx')
