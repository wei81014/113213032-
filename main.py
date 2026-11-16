from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from db import init_db
from routes.author import router as author_router
from routes.editor import router as editor_router

app = FastAPI(title="投稿審查系統")

# 1. 設定 Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="secret-key-for-submission-app",
    max_age=86400,
    same_site="lax",
    https_only=False,
)

# 2. 初始化資料庫
init_db()

# 3. 註冊 APIRouter 模組
app.include_router(author_router, prefix="/author")
app.include_router(editor_router, prefix="/editor")

templates = Jinja2Templates(directory="templates")

# 首頁：自動依據 Session 角色導向對應頁面
@app.get("/")
def index(request: Request):
    role = request.session.get("role", "author")
    if "author_name" not in request.session:
        request.session["author_name"] = "王小明"
    if role == "editor":
        return RedirectResponse(url="/editor/", status_code=303)
    return RedirectResponse(url="/author/", status_code=303)

# 切換角色與設定作者名稱
@app.post("/switch-role")
def switch_role(
    request: Request,
    role: str = Form(...),
    author_name: str = Form("王小明")
):
    request.session["role"] = role
    if author_name.strip():
        request.session["author_name"] = author_name.strip()
    if role == "editor":
        return RedirectResponse(url="/editor/", status_code=303)
    return RedirectResponse(url="/author/", status_code=303)
