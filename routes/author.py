import sqlite3
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 查看投稿稿件清單
@router.get("/")
def author_list(request: Request, db: sqlite3.Connection = Depends(get_db)):
    author_name = request.session.get("author_name", "王小明")
    request.session["role"] = "author"
    
    articles = db.execute(
        "SELECT * FROM articles WHERE author = ? ORDER BY id DESC",
        (author_name,)
    ).fetchall()
    
    return templates.TemplateResponse(
        request=request,
        name="author_list.html",
        context={
            "articles": articles,
            "role": "author",
            "author_name": author_name
        }
    )

# 顯示新增稿件表單
@router.get("/new")
def new_article_form(request: Request):
    author_name = request.session.get("author_name", "王小明")
    return templates.TemplateResponse(
        request=request,
        name="author_form.html",
        context={
            "article": None,
            "role": "author",
            "author_name": author_name
        }
    )

# 處理新增投稿 (狀態預設為 '編輯中')
@router.post("/new")
def create_article(
    request: Request,
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db: sqlite3.Connection = Depends(get_db)
):
    author_name = request.session.get("author_name", "王小明")
    db.execute(
        "INSERT INTO articles (author, category, title, content, status) VALUES (?, ?, ?, ?, '編輯中')",
        (author_name, category, title, content)
    )
    db.commit()
    return RedirectResponse(url="/author/", status_code=303)

# 顯示編輯稿件表單 (僅限狀態為 '編輯中')
@router.get("/edit/{article_id}")
def edit_article_form(request: Request, article_id: int, db: sqlite3.Connection = Depends(get_db)):
    author_name = request.session.get("author_name", "王小明")
    article = db.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    
    if not article or article["status"] != "編輯中":
        raise HTTPException(status_code=400, detail="僅能編輯狀態為「編輯中」的稿件")
        
    return templates.TemplateResponse(
        request=request,
        name="author_form.html",
        context={
            "article": article,
            "role": "author",
            "author_name": author_name
        }
    )

# 處理更新稿件內容
@router.post("/edit/{article_id}")
def update_article(
    article_id: int,
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db: sqlite3.Connection = Depends(get_db)
):
    db.execute(
        "UPDATE articles SET category = ?, title = ?, content = ? WHERE id = ? AND status = '編輯中'",
        (category, title, content, article_id)
    )
    db.commit()
    return RedirectResponse(url="/author/", status_code=303)

# 刪除編輯中稿件
@router.post("/delete/{article_id}")
def delete_article(article_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute(
        "DELETE FROM articles WHERE id = ? AND status = '編輯中'",
        (article_id,)
    )
    db.commit()
    return RedirectResponse(url="/author/", status_code=303)

# 送出投稿：編輯中 => 審查中
@router.post("/submit/{article_id}")
def submit_article(article_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute(
        "UPDATE articles SET status = '審查中' WHERE id = ? AND status = '編輯中'",
        (article_id,)
    )
    db.commit()
    return RedirectResponse(url="/author/", status_code=303)
