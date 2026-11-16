import sqlite3

DB_NAME = "submissions.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 建立稿件資料表，狀態預設為 '編輯中'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT '編輯中'
        )
    """)
    conn.commit()
    conn.close()

# 提供給 FastAPI Depends 使用的資料庫連線產生器
def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 讓查詢結果可用欄位名稱取值
    try:
        yield conn
    finally:
        conn.close()
