import os
import sqlite3
import time
import threading
import shlex
from dotenv import load_dotenv
import telebot

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN이 .env 파일에 설정되지 않았습니다.")

bot = telebot.TeleBot(TOKEN)

# 2. 데이터베이스 초기화 및 연결 함수


def init_db():
    """DB 파일과 테이블이 없으면 자동으로 생성하며, 필요한 컬럼을 관리합니다."""
    conn = sqlite3.connect("study.db")
    cur = conn.cursor()

    # 문장 테이블 생성
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT NOT NULL,
            words TEXT NOT NULL,
            sent_count INTEGER DEFAULT 0,
            last_sent_at INTEGER DEFAULT 0
        )
    ''')

    # 설정 테이블 생성
    cur.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # 기본 설정값 삽입
    cur.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES ('interval', '60')")
    cur.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES ('chat_id', NULL)")

    conn.commit()
    conn.close()


def get_db():
    return sqlite3.connect("study.db", check_same_thread=False)


@bot.message_handler(func=lambda m: m.text.startswith('!'))
def handle_cli_commands(message):
    try:
        conn = get_db()
        cur = conn.cursor()
        # 사용자의 chat_id를 자동으로 설정에 업데이트
        cur.execute(
            "UPDATE settings SET value = ? WHERE key = 'chat_id'", (str(message.chat.id),))
        conn.commit()

        args = shlex.split(message.text)
        cmd = args[0]

        # [C]reate: !c 원문ㅡ번역
        if cmd == "!c":
            content = " ".join(args[1:])
            origin, trans = content.split('ㅡ')
            cur.execute("INSERT INTO sentences (sentence, words, sent_count, last_sent_at) VALUES (?, ?, 0, 0)",
                        (origin.strip(), trans.strip()))
            conn.commit()
            bot.reply_to(message, f"✅ [Created] ID: {cur.lastrowid}")

        # [R]ead: !r id
        elif cmd == "!r":
            target_id = args[1]
            cur.execute(
                "SELECT id, sentence, words FROM sentences WHERE id = ?", (target_id,))
            r = cur.fetchone()
            msg = f"🔍 [ID {r[0]}]\n원문: {r[1]}\n번역: {r[2]}" if r else "❌ 해당 ID를 찾을 수 없습니다."
            bot.reply_to(message, msg)

        # [U]pdate: !u id 원문ㅡ번역
        elif cmd == "!u":
            target_id = args[1]
            content = " ".join(args[2:])
            origin, trans = content.split('ㅡ')
            cur.execute("UPDATE sentences SET sentence = ?, words = ? WHERE id = ?",
                        (origin.strip(), trans.strip(), target_id))
            conn.commit()
            bot.reply_to(message, f"🆙 [Updated] ID: {target_id}")

        # [D]elete: !d id
        elif cmd == "!d":
            target_id = args[1]
            cur.execute("DELETE FROM sentences WHERE id = ?", (target_id,))
            conn.commit()
            bot.reply_to(message, f"🗑️ [Deleted] ID: {target_id}")

        # [Set]ting: !set [초단위]
        elif cmd == "!set":
            seconds = args[1]
            cur.execute(
                "UPDATE settings SET value = ? WHERE key = 'interval'", (seconds,))
            conn.commit()
            bot.reply_to(message, f"⏱️ [Config] 발송 주기가 {seconds}초로 설정되었습니다.")

        # [Ls] List: !ls
        elif cmd == "!ls":
            cur.execute(
                "SELECT id, sentence, words, sent_count FROM sentences ORDER BY id ASC")
            rows = cur.fetchall()
            if not rows:
                bot.reply_to(message, "📋 목록이 비어 있습니다.")
            else:
                res = "\n".join([f"[{r[0]}] {r[1]} (발송:{r[3]})" for r in rows])
                bot.reply_to(message, f"📋 [전체 목록]\n{res[:4000]}")

    except Exception as e:
        bot.reply_to(message, "⚠️ 형식 오류!\n!c 원문ㅡ번역 / !u ID 원문ㅡ번역 / !set 초")

# 4. 발송 엔진 (마지막 발송 시간 기반 순회)


def delivery_engine():
    while True:
        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute("SELECT value FROM settings WHERE key = 'interval'")
            interval = int(cur.fetchone()[0])
            cur.execute("SELECT value FROM settings WHERE key = 'chat_id'")
            res = cur.fetchone()
            chat_id = res[0] if res and res[0] else None

            if chat_id:
                cur.execute(
                    "SELECT id, sentence, words FROM sentences ORDER BY last_sent_at ASC, id ASC LIMIT 1")
                row = cur.fetchone()

                if row:
                    sid, sent, trans = row
                    clean_msg = f"{sent}\n{trans}"
                    bot.send_message(chat_id, clean_msg)

                    cur.execute("UPDATE sentences SET sent_count = sent_count + 1, last_sent_at = ? WHERE id = ?",
                                (int(time.time()), sid))
                    conn.commit()

            time.sleep(interval)
        except Exception as e:
            print(f"Engine Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    init_db()
    print("Bot is running...")
    threading.Thread(target=delivery_engine, daemon=True).start()
    bot.polling(none_stop=True)
