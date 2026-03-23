import streamlit as st
import re

# --- 1. Terminal Aesthetic CSS ---
def apply_hacker_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
        .terminal-box { border: 1px solid #00FF41; padding: 20px; background: rgba(0, 20, 0, 0.9); box-shadow: 0 0 15px #00FF41; margin-bottom: 25px; }
        .stTextInput input { background-color: #000 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. Mission Databases ---

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
    {"lvl": 21, "task": "Check disk space usage (human-readable).", "valid": [r"^df\s+-h$"], "hint": "df -h"},
    {"lvl": 22, "task": "Check size of 'infra' directory.", "valid": [r"^du\s+-sh\s+infra$"], "hint": "du -sh infra"},
    {"lvl": 23, "task": "Display system date/time.", "valid": [r"^date$"], "hint": "date"},
    {"lvl": 24, "task": "Kill process ID 1234.", "valid": [r"^kill\s+1234$"], "hint": "kill 1234"},
    {"lvl": 25, "task": "Sort 'list.txt' content.", "valid": [r"^sort\s+list\.txt$"], "hint": "sort list.txt"},
    {"lvl": 26, "task": "Count lines in 'config.tf'.", "valid": [r"^wc\s+-l\s+config\.tf$"], "hint": "wc -l config.tf"},
    {"lvl": 27, "task": "Search for 'config.tf' in current tree.", "valid": [r"^find\s+\.\s+-name\s+config\.tf$"], "hint": "find . -name config.tf"},
    {"lvl": 28, "task": "Filter 'config.tf' for 'resource' and count them.", "valid": [r"^grep\s+resource\s+config\.tf\s*\|\s*wc\s+-l$"], "hint": "grep | wc"},
    {"lvl": 29, "task": "Change owner of 'scan.sh' to 'admin'.", "valid": [r"^chown\s+admin\s+scan\.sh$"], "hint": "chown admin scan.sh"},
    {"lvl": 30, "task": "Combine 'f1' and 'f2' into 'all.txt'.", "valid": [r"^cat\s+f1\s+f2\s*>\s*all\.txt$"], "hint": "cat > all"}
]

CHECKOV_MISSIONS = [
    {"lvl": 1, "task": "Scan directory '.' and ignore passing checks.", "valid": [r".*--quiet.*"], "hint": "--quiet"},
    {"lvl": 2, "task": "Scan directory '.' but ensure the exit code is always 0.", "valid": [r".*--soft-fail.*"], "hint": "--soft-fail"},
    {"lvl": 3, "task": "Run only checks with 'HIGH' or 'CRITICAL' severity.", "valid": [r".*--check\s+(high,critical|critical,high).*"], "hint": "--check HIGH,CRITICAL"},
    {"lvl": 4, "task": "Skip checks with 'LOW' severity.", "valid": [r".*--skip-check\s+low.*"], "hint": "--skip-check LOW"},
    {"lvl": 5, "task": "Soft-fail only if the severity is 'MEDIUM'.", "valid": [r".*--soft-fail-on\s+medium.*"], "hint": "--soft-fail-on MEDIUM"},
    {"lvl": 6, "task": "Hard-fail the scan if a 'CRITICAL' check fails.", "valid": [r".*--hard-fail-on\s+critical.*"], "hint": "--hard-fail-on CRITICAL"},
    {"lvl": 7, "task": "Enable scanning for secrets in your IaC files.", "valid": [r".*--enable-secret-scan.*"], "hint": "--enable-secret-scan"},
    {"lvl": 8, "task": "Show only the summary without the detailed code blocks.", "valid": [r".*--compact.*"], "hint": "--compact"},
    {"lvl": 9, "task": "Scan directory '.' and output results in 'sarif' format.", "valid": [r".*(-o|--output)\s+sarif.*"], "hint": "-o sarif"},
    {"lvl": 10, "task": "Limit the scan specifically to 'terraform' files.", "valid": [r".*--framework\s+terraform.*"], "hint": "--framework terraform"},
    {"lvl": 11, "task": "Scan using a specific configuration file named 'config.yaml'.", "valid": [r".*--config-file\s+config\.yaml.*"], "hint": "--config-file config.yaml"},
    {"lvl": 12, "task": "Exclude the 'node_modules' directory from the scan.", "valid": [r".*--skip-path\s+node_modules.*"], "hint": "--skip-path node_modules"},
    {"lvl": 13, "task": "Point to an external checks directory named 'my_checks'.", "valid": [r".*--external-checks-dir\s+my_checks.*"], "hint": "--external-checks-dir my_checks"},
    {"lvl": 14, "task": "Download external modules before scanning.", "valid": [r".*--download-external-modules\s+true.*"], "hint": "--download-external-modules true"},
    {"lvl": 15, "task": "Map plan file results back to source code using repo root '/app'.", "valid": [r".*--repo-root-for-plan-enrichment\s+/app.*"], "hint": "--repo-root-for-plan-enrichment"},
    {"lvl": 16, "task": "List all available checks for the 'kubernetes' framework.", "valid": [r".*--list.*--framework\s+kubernetes.*"], "hint": "--list --framework kubernetes"},
    {"lvl": 17, "task": "Scan directory '.' and create a new baseline file.", "valid": [r".*--create-baseline.*"], "hint": "--create-baseline"},
    {"lvl": 18, "task": "Run scan against an existing baseline file '.checkov.baseline'.", "valid": [r".*--baseline\s+\.checkov\.baseline.*"], "hint": "--baseline .checkov.baseline"},
    {"lvl": 19, "task": "Evaluate variables using a file named 'production.tfvars'.", "valid": [r".*--var-file\s+production\.tfvars.*"], "hint": "--var-file production.tfvars"},
    {"lvl": 20, "task": "Display the current version of Checkov.", "valid": [r".*(-v|--version).*"], "hint": "-v"},
    {"lvl": 21, "task": "Run scan and output to a specific directory '/reports'.", "valid": [r".*--output-file-path\s+/reports.*"], "hint": "--output-file-path /reports"},
    {"lvl": 22, "task": "Scan directory '.' but skip 'secrets' and 'arm' frameworks.", "valid": [r".*--skip-framework\s+(secrets,arm|arm,secrets).*"], "hint": "--skip-framework secrets,arm"},
    {"lvl": 23, "task": "Run only the check with ID 'CKV_AWS_123'.", "valid": [r".*--check\s+ckv_aws_123.*"], "hint": "--check CKV_AWS_123"},
    {"lvl": 24, "task": "Scan a Dockerfile using the '--file' flag.", "valid": [r".*(-f|--file)\s+Dockerfile.*"], "hint": "-f Dockerfile"},
    {"lvl": 25, "task": "Output results in both 'cli' and 'json' formats.", "valid": [r".*(-o|--output)\s+(cli,json|json,cli).*"], "hint": "-o cli,json"},
    {"lvl": 26, "task": "Set a severity threshold for 'MEDIUM' and higher.", "valid": [r".*--check\s+medium.*"], "hint": "--check MEDIUM"},
    {"lvl": 27, "task": "Scan and show all config settings with '--show-config'.", "valid": [r".*--show-config.*"], "hint": "--show-config"},
    {"lvl": 28, "task": "Enable deep analysis for Terraform plan enrichment.", "valid": [r".*--deep-analysis.*"], "hint": "--deep-analysis"},
    {"lvl": 29, "task": "Download remote policies from a Git repo 'github.com/org/policies'.", "valid": [r".*--external-checks-git\s+.*github\.com/org/policies.*"], "hint": "--external-checks-git"},
    {"lvl": 30, "task": "Final Boss: Scan '.', quiet, compact, and hard-fail on 'HIGH'.", "valid": [r".*--quiet.*--compact.*--hard-fail-on\s+high.*"], "hint": "--quiet --compact --hard-fail-on HIGH"}
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
    if st.button("RELOAD SYSTEM"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

tab_linux, tab_checkov, tab_ref = st.tabs(["📂 LINUX QUEST", "🛡️ CHECKOV FLAGS", "📖 CLI REFERENCE"])

with tab_ref:
    st.header("Checkov CLI Parameter Guide")
    st.info("Reference: https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Core Flags")
        st.markdown("""
        * `-d, --directory`: Directory to scan.
        * `-f, --file`: Specific file to scan.
        * `--quiet`: Display only failed checks.
        * `--compact`: Remove code blocks from output.
        * `--soft-fail`: Return exit code 0 regardless of failures.
        * `--soft-fail-on [SEV/ID]`: Soft-fail specific severities.
        * `--hard-fail-on [SEV/ID]`: Hard-fail specific severities.
        """)
    with col2:
        st.subheader("Advanced Flags")
        st.markdown("""
        * `--framework`: Limit to `terraform`, `kubernetes`, `aws_sam`, etc.
        * `--check`: Run specific check IDs or Severities.
        * `--skip-check`: Exclude check IDs or Severities.
        * `--enable-secret-scan`: Scan for credentials.
        * `--create-baseline`: Create a file to ignore current failures.
        * `--var-file`: Path to variables file (e.g. `.tfvars`).
        * `--repo-root-for-plan-enrichment`: Path to root code for plan mapping.
        """)

def play_level(missions, index_key):
    idx = st.session_state[index_key]
    if idx >= len(missions):
        st.success("SECTOR SECURED.")
        return
    current = missions[idx]
    st.markdown(f'<div class="terminal-box"><b>LEVEL {idx + 1} / {len(missions)}:</b><br>{current["task"]}</div>', unsafe_allow_html=True)
    if st.button("HINT", key=f"hint_{index_key}_{idx}"): st.toast(f"HINT: {current['hint']}")
    cmd = st.text_input("user@terminal:~$ ", key=f"in_{index_key}_{idx}").strip()
    if not st.session_state.success:
        if st.button("EXECUTE", key=f"ex_{index_key}_{idx}"):
            # Note: Using case-insensitive regex for flags
            if any(re.search(p, cmd.lower()) for p in current['valid']):
                st.session_state.success = True
                st.rerun()
            else:
                st.error("SYNTAX ERROR: FLAG NOT FOUND OR INCORRECT")
                st.session_state.health -= 1
                st.rerun()
    else:
        st.success("FLAG ACCEPTED")
        if st.button("NEXT LEVEL ➡️", key=f"nxt_{index_key}_{idx}"):
            st.session_state[index_key] += 1
            st.session_state.success = False
            st.rerun()

with tab_linux: play_level(LINUX_MISSIONS, 'linux_idx')
with tab_checkov: play_level(CHECKOV_MISSIONS, 'checkov_idx')
