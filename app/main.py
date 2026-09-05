"""
Главный модуль FastAPI приложения PyForge — Интерактивный комбайн для разработчиков Python.
"""

from fastapi import FastAPI, HTTPException, Query, Response, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List, Dict, Any

from .data.architecture import ARCHITECTURE_TOPICS
from .data.frameworks import FRAMEWORKS_DATA
from .data.databases import DATABASES_TOPICS
from .data.packaging import PACKAGING_TOPICS
from .data.tools import TOOLS_TOPICS
from .data.snippets import SNIPPETS_DATA
from .data.generator_templates import PROJECT_TEMPLATES
from .services.scaffolder import ScaffolderService
from .services.sandbox import SandboxService
from .services.ai_scout import AIScoutService
from .services.gamification import GamificationService
from .services.practice_engine import PracticeEngineService
from .services.live_error_mentor import LiveErrorMentorService
from .services.library_task_generator import LibraryTaskGeneratorService
from .services.vscode_bridge import VSCodeBridgeService
from .services.auth_service import AuthService
from .services.leaderboard_service import LeaderboardService
from .services.forum_service import ForumService
from .services.ideas_service import IdeasService

app = FastAPI(
    title="PyForge: Ultimate Python App Studio & Knowledge Hub",
    description="Интерактивный справочник, генератор проектов и песочница для Python разработчиков",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_token(authorization: Optional[str] = None, token_param: Optional[str] = None) -> Optional[str]:
    if authorization:
        clean = authorization.strip()
        if clean.lower().startswith("bearer "):
            return clean[7:].strip()
        return clean
    return token_param

# Pydantic модели запросов
class RunCodeRequest(BaseModel):
    code: str
    timeout: Optional[float] = 5.0

class GenerateDirectoryRequest(BaseModel):
    template_id: str
    target_directory: str
    project_name: Optional[str] = None

class AIScoutRequest(BaseModel):
    query: str
    mode: Optional[str] = "smart"
    llm_config: Optional[Dict[str, Any]] = None

class SubmitSolutionRequest(BaseModel):
    task_id: str
    code: str

class GenerateTaskRequest(BaseModel):
    topic: Optional[str] = "базовые алгоритмы"
    difficulty: Optional[str] = "Middle"

class RandomLibraryTaskRequest(BaseModel):
    library: str
    difficulty: Optional[str] = None

class BuyTitleRequest(BaseModel):
    title_id: str

class SetActiveTitleRequest(BaseModel):
    title_id: str

class MentorInspectRequest(BaseModel):
    code: str

class InspectFileRequest(BaseModel):
    file_path: str

class InspectWorkspaceRequest(BaseModel):
    workspace_dir: str
    max_files: Optional[int] = 30

class ApplyFixRequest(BaseModel):
    file_path: str
    fixed_code: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LogoutRequest(BaseModel):
    token: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    new_password: Optional[str] = None

class CreateTopicRequest(BaseModel):
    title: str
    category: str
    content: str
    tags: Optional[List[str]] = None

class AddCommentRequest(BaseModel):
    topic_id: str
    content: str

class UpvoteTopicRequest(BaseModel):
    topic_id: str

class CreateIdeaRequest(BaseModel):
    title: str
    description: str
    category: Optional[str] = "general"

class VoteIdeaRequest(BaseModel):
    idea_id: str

# --- AUTH & USER PROFILE ---

@app.post("/api/auth/register")
async def auth_register(req: RegisterRequest):
    try:
        return AuthService.register(req.username, req.password, req.display_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def auth_login(req: LoginRequest):
    try:
        return AuthService.login(req.username, req.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/auth/me")
async def auth_me(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    user = AuthService.get_user_by_token(t)
    if not user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    return {"success": True, "user": AuthService.sanitize_user(user)}

@app.post("/api/auth/logout")
async def auth_logout(req: Optional[LogoutRequest] = None, authorization: Optional[str] = Header(None)):
    t = extract_token(authorization, req.token if req else None)
    if t:
        AuthService.logout(t)
    return {"success": True}

@app.put("/api/auth/profile")
async def auth_update_profile(req: UpdateProfileRequest, authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    if not t:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        return AuthService.update_profile(
            token=t,
            display_name=req.display_name,
            avatar=req.avatar,
            bio=req.bio,
            new_password=req.new_password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- LEADERBOARD ---

@app.get("/api/leaderboard")
async def get_leaderboard(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    user = AuthService.get_user_by_token(t)
    current_username = user.get("username") if user else None
    return LeaderboardService.get_leaderboard(current_username=current_username)

# --- FORUM ---

@app.get("/api/forum/categories")
async def get_forum_categories():
    return ForumService.get_categories()

@app.get("/api/forum/topics")
async def list_forum_topics(category: Optional[str] = None, search: Optional[str] = None):
    return ForumService.list_topics(category=category, search=search)

@app.get("/api/forum/topics/{topic_id}")
async def get_forum_topic_detail(topic_id: str):
    topic = ForumService.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема форума не найдена")
    return topic

@app.post("/api/forum/topics/create")
async def create_forum_topic(req: CreateTopicRequest, authorization: Optional[str] = Header(None)):
    t = extract_token(authorization)
    user = AuthService.get_user_by_token(t)
    username = user["username"] if user else "Аноним"
    try:
        return ForumService.create_topic(
            title=req.title,
            category=req.category,
            content=req.content,
            author_username=username,
            tags=req.tags
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/forum/comments/create")
async def add_forum_comment(req: AddCommentRequest, authorization: Optional[str] = Header(None)):
    t = extract_token(authorization)
    user = AuthService.get_user_by_token(t)
    username = user["username"] if user else "Аноним"
    try:
        return ForumService.add_comment(
            topic_id=req.topic_id,
            content=req.content,
            author_username=username
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/forum/upvote")
async def upvote_forum_topic(req: UpvoteTopicRequest, authorization: Optional[str] = Header(None)):
    t = extract_token(authorization)
    user = AuthService.get_user_by_token(t)
    username = user["username"] if user else "guest_user"
    try:
        return ForumService.upvote_topic(req.topic_id, username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- CREATOR IDEAS HUB ---

@app.get("/api/ideas/list")
async def list_ideas(category: Optional[str] = None, status: Optional[str] = None, sort_by: Optional[str] = "popular"):
    return IdeasService.list_ideas(category=category, status=status, sort_by=sort_by or "popular")

@app.post("/api/ideas/create")
async def create_idea(req: CreateIdeaRequest, authorization: Optional[str] = Header(None)):
    t = extract_token(authorization)
    user = AuthService.get_user_by_token(t)
    username = user["username"] if user else "Аноним"
    try:
        return IdeasService.submit_idea(
            title=req.title,
            description=req.description,
            category=req.category or "general",
            author_username=username
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ideas/vote")
async def vote_idea(req: VoteIdeaRequest, authorization: Optional[str] = Header(None)):
    t = extract_token(authorization)
    user = AuthService.get_user_by_token(t)
    username = user["username"] if user else "guest_user"
    try:
        return IdeasService.vote_idea(req.idea_id, username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- ПРАКТИКА И ГЕЙМИФИКАЦИЯ ЭНДПОИНТЫ ---

@app.get("/api/practice/profile")
async def get_user_profile(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    return GamificationService.get_full_profile(t)

@app.get("/api/practice/tasks")
async def get_practice_tasks(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    return PracticeEngineService.list_tasks(t)

@app.get("/api/practice/libraries-list")
async def get_practice_libraries_list():
    return LibraryTaskGeneratorService.get_supported_libraries()

@app.post("/api/practice/random-by-library")
async def generate_random_by_library(req: RandomLibraryTaskRequest):
    task = LibraryTaskGeneratorService.generate_random_task(req.library, req.difficulty)
    return {"success": True, "task": task}

@app.post("/api/practice/submit")
async def submit_practice_solution(req: SubmitSolutionRequest, authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    try:
        return PracticeEngineService.submit_solution(req.task_id, req.code, t)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/practice/generate-task")
async def generate_ai_practice_task(req: GenerateTaskRequest):
    return PracticeEngineService.generate_ai_task(req.topic or "алгоритмы", req.difficulty or "Middle")

@app.post("/api/practice/buy-title")
async def buy_title_endpoint(req: BuyTitleRequest, authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    try:
        return GamificationService.buy_title(req.title_id, t)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/practice/set-active-title")
async def set_active_title_endpoint(req: SetActiveTitleRequest, authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)):
    t = extract_token(authorization, token)
    try:
        return GamificationService.set_active_title(req.title_id, t)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- РЕАЛТАЙМ ИИ-НАСТАВНИК ОШИБОК & VS CODE МОСТ ---

@app.post("/api/mentor/inspect")
async def inspect_code_live(req: MentorInspectRequest):
    return LiveErrorMentorService.inspect_code(req.code)

@app.get("/api/vscode/status")
async def get_vscode_bridge_status():
    return VSCodeBridgeService.get_status()

@app.post("/api/vscode/inspect-file")
async def inspect_vscode_file(req: InspectFileRequest):
    return VSCodeBridgeService.inspect_file(req.file_path)

@app.post("/api/vscode/inspect-workspace")
async def inspect_vscode_workspace(req: InspectWorkspaceRequest):
    return VSCodeBridgeService.inspect_workspace(req.workspace_dir, req.max_files or 30)

@app.post("/api/vscode/apply-fix")
async def apply_vscode_fix(req: ApplyFixRequest):
    return VSCodeBridgeService.apply_file_fix(req.file_path, req.fixed_code)

# --- AI SCOUT ЭНДПОИНТЫ ---

@app.get("/api/ai/suggestions")
async def get_ai_suggestions():
    return AIScoutService.get_suggestions()

@app.post("/api/ai/scout")
async def scout_libraries(req: AIScoutRequest):
    return AIScoutService.search(req.query, mode=req.mode or "smart", llm_config=req.llm_config)

# --- API ЭНДПОИНТЫ ---

@app.get("/api/overview")
async def get_overview():
    return {
        "title": "PyForge — Интерактивная платформа для создания приложений на Python",
        "stats": {
            "frameworks_count": len(FRAMEWORKS_DATA),
            "architecture_guides": len(ARCHITECTURE_TOPICS),
            "databases_guides": len(DATABASES_TOPICS),
            "packaging_guides": len(PACKAGING_TOPICS),
            "tools_guides": len(TOOLS_TOPICS),
            "snippets_count": len(SNIPPETS_DATA),
            "templates_count": len(PROJECT_TEMPLATES)
        }
    }

@app.get("/api/architecture")
async def get_architecture():
    return ARCHITECTURE_TOPICS

@app.get("/api/frameworks")
async def get_frameworks(category: Optional[str] = None):
    if category:
        return [f for f in FRAMEWORKS_DATA if f.get("category") == category]
    return FRAMEWORKS_DATA

@app.get("/api/databases")
async def get_databases():
    return DATABASES_TOPICS

@app.get("/api/packaging")
async def get_packaging():
    return PACKAGING_TOPICS

@app.get("/api/tools")
async def get_tools():
    return TOOLS_TOPICS

@app.get("/api/snippets")
async def get_snippets(category: Optional[str] = None, tag: Optional[str] = None):
    results = SNIPPETS_DATA
    if category:
        results = [s for s in results if s.get("category") == category]
    if tag:
        tag_lower = tag.lower()
        results = [s for s in results if any(tag_lower in t.lower() for t in s.get("tags", []))]
    return results

@app.get("/api/templates")
async def list_templates():
    return ScaffolderService.list_templates()

@app.get("/api/templates/{template_id}")
async def get_template_detail(template_id: str):
    template = ScaffolderService.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return template

@app.post("/api/scaffold/directory")
async def generate_to_directory(req: GenerateDirectoryRequest):
    try:
        result = ScaffolderService.generate_to_directory(
            template_id=req.template_id,
            target_dir=req.target_directory,
            project_name=req.project_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/scaffold/download/{template_id}")
async def download_zip(template_id: str, project_name: Optional[str] = "my_python_app"):
    try:
        zip_buffer = ScaffolderService.generate_zip_bytes(template_id, project_name)
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{project_name}.zip"'}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sandbox/run")
async def run_sandbox_code(req: RunCodeRequest):
    return SandboxService.run_code(req.code, req.timeout or 5.0)

@app.get("/api/search")
async def search_all(q: str = Query(..., min_length=2)):
    query = q.lower()
    results = []

    # Поиск по фреймворкам
    for f in FRAMEWORKS_DATA:
        if query in f["name"].lower() or query in f["description"].lower() or query in f.get("install", "").lower():
            results.append({
                "type": "Фреймворк",
                "id": f["id"],
                "tab": "frameworks",
                "title": f["name"],
                "category": f["category"],
                "snippet": f["description"][:120] + "..."
            })

    # Поиск по архитектуре
    for a in ARCHITECTURE_TOPICS:
        if query in a["title"].lower() or query in a["summary"].lower() or query in a["content"].lower():
            results.append({
                "type": "Архитектура",
                "id": a["id"],
                "tab": "architecture",
                "title": a["title"],
                "category": a.get("category", "architecture"),
                "snippet": a["summary"]
            })

    # Поиск по базам данных
    for d in DATABASES_TOPICS:
        if query in d["title"].lower() or query in d["summary"].lower() or query in d["content"].lower():
            results.append({
                "type": "Базы данных",
                "id": d["id"],
                "tab": "databases",
                "title": d["title"],
                "category": d.get("category", "databases"),
                "snippet": d["summary"]
            })

    # Поиск по упаковке
    for p in PACKAGING_TOPICS:
        if query in p["title"].lower() or query in p["summary"].lower() or query in p["content"].lower():
            results.append({
                "type": "Сборка (.EXE)",
                "id": p["id"],
                "tab": "packaging",
                "title": p["title"],
                "category": p.get("category", "packaging"),
                "snippet": p["summary"]
            })

    # Поиск по инструментам
    for t in TOOLS_TOPICS:
        if query in t["title"].lower() or query in t["summary"].lower() or query in t["content"].lower():
            results.append({
                "type": "Инструменты",
                "id": t["id"],
                "tab": "tools",
                "title": t["title"],
                "category": t.get("category", "tools"),
                "snippet": t["summary"]
            })

    # Поиск по сниппетам
    for s in SNIPPETS_DATA:
        tags_str = " ".join(s.get("tags", [])).lower()
        if query in s["title"].lower() or query in s["description"].lower() or query in tags_str or query in s["code"].lower():
            results.append({
                "type": "Сниппет",
                "id": s["id"],
                "tab": "snippets",
                "title": s["title"],
                "category": s["category"],
                "snippet": s["description"]
            })

    return results

# Подключение статических файлов и главной страницы
from fastapi.responses import FileResponse

static_dir = None
for candidate in [
    Path(__file__).resolve().parent / "static",
    Path("app/static").resolve(),
    Path("static").resolve()
]:
    if candidate.exists() and (candidate / "index.html").exists():
        static_dir = candidate
        break

if not static_dir:
    static_dir = Path(__file__).resolve().parent / "static"

@app.get("/")
async def serve_index():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"status": "ok", "message": "PyForge Studio is active. Static files directory: " + str(static_dir)}

@app.get("/manifest.json")
async def serve_manifest():
    manifest_path = static_dir / "manifest.json"
    if manifest_path.exists():
        return FileResponse(str(manifest_path), media_type="application/manifest+json")
    return {}

if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
