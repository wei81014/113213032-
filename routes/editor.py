import sqlite3
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 查看待審查清單 (篩選狀態為 '審查中')
@router.get("/")
def editor_list(request: Request, db: sqlite3.Connection = Depends(get_db)):
    author_name = request.session.get("author_name", "王小明")
    request.session["role"] = "editor"
    
    pending_articles = db.execute(
        "SELECT * FROM articles WHERE status = '審查中' ORDER BY id ASC"
    ).fetchall()
    
    return templates.TemplateResponse(
        "editor_list.html",
        {
            "request": request,
            "articles": pending_articles,
            "role": "editor",
            "author_name": author_name
        }
    )

# 查看稿件內容
@router.get("/review/{article_id}")
def review_article(request: Request, article_id: int, db: sqlite3.Connection = Depends(get_db)):
    author_name = request.session.get("author_name", "王小明")
    article = db.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    
    if not article:
        raise HTTPException(status_code=404, detail="找不到該稿件")
        
    return templates.TemplateResponse(
        "editor_review.html",
        {
            "request": request,
            "article": article,
            "role": "editor",
            "author_name": author_name
        }
    )

# 選擇通過：審查中 => 已通過
@router.post("/approve/{article_id}")
def approve_article(article_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute(
        "UPDATE articles SET status = '已通過' WHERE id = ? AND status = '審查中'",
        (article_id,)
    )
    db.commit()
    return RedirectResponse(url="/editor/", status_code=303)

# 退回稿件：審查中 => 編輯中
@router.post("/reject/{article_id}")
def reject_article(article_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute(
        "UPDATE articles SET status = '編輯中' WHERE id = ? AND status = '審查中'",
        (article_id,)
    )
    db.commit()
    return RedirectResponse(url="/editor/", status_code=303)
