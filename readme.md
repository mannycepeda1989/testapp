🕹️ Terminal Hero: Command Quest
Welcome to the Terminal Hero training simulator! This Streamlit-based game is designed to take you from a "Script Kiddy" to a "Kernel Overlord" through 25 interactive missions.

🛠️ The Command Reference (Study Guide)
Master these commands to beat the game and improve your real-world workflow.

1. Navigation & Orientation
ls: List files and directories in your current location.

ls -a: List all files, including hidden ones (starting with a .).

pwd: Print Working Directory—shows the full path of where you are.

cd [folder]: Change Directory to enter a folder.

cd ..: Move up one level to the parent directory.

clear: Wipes the terminal screen to give you a fresh start.

2. File & Folder Management
mkdir [name]: Make Directory to create a new folder.

touch [file]: Creates a new, empty file instantly.

cp [source] [dest]: Copy a file from one place to another.

mv [source] [dest]: Move or Rename a file or folder.

rm [file]: Remove a file. Warning: There is no Trash bin in the terminal!

zip [out.zip] [folder]: Compress files or folders into a .zip archive.

chmod +x [file]: Change mode to make a script executable.

3. Reading & Searching
echo "[text]": Prints text back to the terminal.

cat [file]: Displays the entire contents of a file.

head [file]: Shows the first 10 lines of a file.

tail [file]: Shows the last 10 lines of a file.

grep "[pattern]" [file]: Searches for specific text within a file.

man [command]: Opens the Manual for any command.

find . -name "*.txt": Searches the filesystem for files matching a pattern.

4. System & Networking
ping [host]: Tests your connection to a server (like https://www.google.com/search?q=google.com).

ifconfig / ip addr: Displays your network interface and IP address.

top / ps aux: Shows active processes and system resource usage.

5. Advanced: Piping & Redirection (The Boss Levels)
| (The Pipe): Takes the output of the left command and sends it as input to the right command.

Example: ls | wc -l (List files, then count the lines in that list).

> (Redirection): Takes the output of a command and saves it into a file, overwriting the file.

Example: grep "ERROR" log.txt > errors.txt.
