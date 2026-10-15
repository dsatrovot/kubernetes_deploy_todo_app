from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas

#FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Convenient for a learning project. For production, use Alembic migrations.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="A small CRUD API backed by PostgreSQL.",
    lifespan=lifespan,
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@app.get("/api/todos", response_model=list[schemas.TodoResponse])
def list_todos(
    completed: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Todo)
    if completed is not None:
        query = query.filter(models.Todo.is_completed == completed)
    return query.order_by(models.Todo.created_at.desc(), models.Todo.id.desc()).all()


@app.post("/api/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(payload: schemas.TodoCreate, db: Session = Depends(get_db)):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be blank")
    todo = models.Todo(title=title, description=payload.description.strip())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.patch("/api/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, payload: schemas.TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    changes = payload.model_dump(exclude_unset=True)
    if "title" in changes and changes["title"] is not None:
        changes["title"] = changes["title"].strip()
        if not changes["title"]:
            raise HTTPException(status_code=422, detail="Title cannot be blank")
    for field, value in changes.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return Response(status_code=204)


#app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND_DIR / "index.html")
