import json
import datetime
import sys
import subprocess
import os

# 設定
LOG_FILE = 'logs.json'
HEADER_FILE = 'header.md'
FAQ_FILE = 'interview-faq.md'
README_FILE = 'README.md'
MAX_LOGS_IN_README = 10

def add_log(message):
    """logs.json に新しいログを追加する"""
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    
    new_entry = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "message": message
    }
    logs.append(new_entry)
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"Added log to {LOG_FILE}: {message}")

def rebuild_readme():
    """header, logs, faq を組み合わせて README.md を生成する"""
    content = ""
    
    # 1. Header 部分
    if os.path.exists(HEADER_FILE):
        with open(HEADER_FILE, 'r', encoding='utf-8') as f:
            content += f.read() + "\n\n"
    
    # 2. Learning Logs 部分
    content += "## 📝 Recent Learning Logs\n\n"
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            # 最新のものを上に表示（reversed）
            for log in reversed(logs[-MAX_LOGS_IN_README:]):
                content += f"- **{log['date']}**: {log['message']}\n"
    content += "\n"
    
    # 3. Interview FAQ 部分
    content += "## 💬 Interview FAQ (Excerpt)\n\n"
    if os.path.exists(FAQ_FILE):
        with open(FAQ_FILE, 'r', encoding='utf-8') as f:
            content += f.read() + "\n"
            
    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"{README_FILE} has been rebuilt.")

def git_push(message):
    """Git add, commit, push を実行する"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Log: {message}"], check=True)
        # GitHubへのプッシュを有効化
        subprocess.run(["git", "push"], check=True)
        print("Successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_log.py \"Your learning message\"")
        sys.exit(1)
    
    log_msg = sys.argv[1]
    add_log(log_msg)
    rebuild_readme()
    git_push(log_msg)
