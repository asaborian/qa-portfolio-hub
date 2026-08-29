import json
import datetime
import sys
import subprocess
import os

# 設定定数
LOG_FILE = 'learning-logs.json'
HEADER_FILE = 'header.md'
FAQ_FILE = 'interview-faq.md'
README_FILE = 'README.md'
LOGS_MD_FILE = 'learning-logs.md'

MAX_LOGS_IN_README = 5
MAX_FAQ_IN_README = 3

def load_logs():
    """jsonファイルからログを安全に読み込む"""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Failed to load {LOG_FILE}: {e}")
        return []

def add_log(message):
    """logs.json に新しいログを追加して保存する"""
    logs = load_logs()
    new_entry = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "message": message
    }
    logs.append(new_entry)

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    print(f"Added log: {message}")
    return logs

def rebuild_readme(logs):
    """header, logs, faq を組み合わせて README.md を生成する"""
    content_parts = []

    # 1. Header 部分
    if os.path.exists(HEADER_FILE):
        with open(HEADER_FILE, 'r', encoding='utf-8') as f:
            content_parts.append(f.read().strip())

    # 2. Learning Logs 部分
    log_section = ["## 📝 Recent Learning Logs\n"]
    if logs:
        for log in reversed(logs[-MAX_LOGS_IN_README:]):
            log_section.append(f"- **{log['date']}**: {log['message']}")
    log_section.append(f"\n📄 **[すべての学習ログを見る → {LOGS_MD_FILE}]({LOGS_MD_FILE})**")
    content_parts.append("\n".join(log_section))

    # 3. Interview FAQ 部分
    if os.path.exists(FAQ_FILE):
        faq_section = ["## 💬 Interview FAQ\n"]
        with open(FAQ_FILE, 'r', encoding='utf-8') as f:
            faq_text = f.read()

        # READMEに優先掲載したい最重要3問のタイトル文字列
        target_questions = [
            "Q: 就職したらどのように貢献できるか？",
            "Q: 勤務形態に関して合意が必要な条件はあるか？",
            "Q: なぜ37歳実務未経験でITエンジニアを目指すに至ったのか？"
        ]

        # '### ' で分割して各Q&Aブロックを取得
        raw_blocks = faq_text.split('### ')
        faq_blocks = [f"### {b.rstrip()}" for b in raw_blocks if b.startswith('Q:')]

        # 指定タイトルが含まれるブロックを検索して抽出
        excerpt = []
        for q_title in target_questions:
            for block in faq_blocks:
                if q_title in block:
                    excerpt.append(block)
                    break

        # タイトル変更や誤字で3問揃わなかった場合のフォールバック（先頭から順に補填）
        if len(excerpt) < MAX_FAQ_IN_README:
            print(f"Warning: Expected {MAX_FAQ_IN_README} FAQ items by title, but found {len(excerpt)}. Falling back to top items.")
            for block in faq_blocks:
                if block not in excerpt:
                    excerpt.append(block)
                if len(excerpt) == MAX_FAQ_IN_README:
                    break

        faq_section.append("\n\n".join(excerpt))
        faq_section.append(f"\n📄 **[すべての想定質問と回答を見る（全28問） → {FAQ_FILE}]({FAQ_FILE})**")
        content_parts.append("\n".join(faq_section))

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write("\n\n---\n\n".join(content_parts) + "\n")

    print(f"{README_FILE} has been rebuilt.")

def rebuild_learning_logs(logs):
    """全学習ログのマークダウンファイルを生成する"""
    lines = ["# 📝 全学習ログ一覧\n", "[← READMEに戻る](./README.md)\n"]
    for log in reversed(logs):
        lines.append(f"- **{log['date']}**: {log['message']}")

    with open(LOGS_MD_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

def git_push(message):
    """Git add, commit, push を実行する"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Log: {message}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_learning_log.py \"Your learning message\"")
        sys.exit(1)

    log_msg = sys.argv[1]
    current_logs = add_log(log_msg)
    rebuild_readme(current_logs)
    rebuild_learning_logs(current_logs)
    git_push(log_msg)
