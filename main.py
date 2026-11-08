from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from database import SessionLocal
import models
from schemas import TaskCreate, TaskUpdate, TaskResponse


app = FastAPI(title="AgencyOS API")


# ---------------- DATABASE SESSION ----------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------- REQUEST VALIDATION ----------------

class Brief(BaseModel):

    title: str = Field(min_length=1, max_length=100)

    description: str = Field(min_length=1, max_length=1000)

    @field_validator("title", "description", mode="before")
    @classmethod
    def validate_text(cls, value):

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError(
                    "Field cannot be empty or contain only spaces"
                )

        return value


# ---------------- HOME AND HEALTH ----------------

@app.get("/")
def home():
    return {"message": "AgencyOS is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ---------------- CREATE A CLIENT BRIEF ----------------

@app.post("/briefs", status_code=201)
def create_brief(
    brief: Brief,
    db: Session = Depends(get_db)
):

    new_brief = models.BriefModel(
        title=brief.title,
        description=brief.description
    )

    try:
        db.add(new_brief)
        db.commit()
        db.refresh(new_brief)

    except Exception:
        db.rollback()
        raise

    return {
        "id": new_brief.id,
        "title": new_brief.title,
        "description": new_brief.description
    }


# ---------------- RETRIEVE ALL BRIEFS ----------------

@app.get("/briefs")
def get_briefs(db: Session = Depends(get_db)):

    briefs = db.query(models.BriefModel).order_by(
        models.BriefModel.id
    ).all()

    return [
        {
            "id": brief.id,
            "title": brief.title,
            "description": brief.description
        }
        for brief in briefs
    ]


# ---------------- RETRIEVE ONE BRIEF ----------------

@app.get("/briefs/{brief_id}")
def get_brief(
    brief_id: int,
    db: Session = Depends(get_db)
):

    brief = db.get(models.BriefModel, brief_id)

    if brief is None:
        raise HTTPException(
            status_code=404,
            detail="Brief not found"
        )

    return {
        "id": brief.id,
        "title": brief.title,
        "description": brief.description
    }


# ---------------- UPDATE AN EXISTING BRIEF ----------------

@app.put("/briefs/{brief_id}")
def update_brief(
    brief_id: int,
    updated_data: Brief,
    db: Session = Depends(get_db)
):

    brief = db.get(models.BriefModel, brief_id)

    if brief is None:
        raise HTTPException(
            status_code=404,
            detail="Brief not found"
        )

    brief.title = updated_data.title
    brief.description = updated_data.description

    try:
        db.commit()
        db.refresh(brief)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Brief updated successfully",
        "brief": {
            "id": brief.id,
            "title": brief.title,
            "description": brief.description
        }
    }


# ---------------- DELETE AN EXISTING BRIEF ----------------

@app.delete(
    "/briefs/{brief_id}",
    status_code=200,
    responses={
        404: {"description": "Brief not found"}
    }
)
def delete_brief(
    brief_id: int,
    db: Session = Depends(get_db)
):

    brief = db.get(models.BriefModel, brief_id)

    if brief is None:
        raise HTTPException(
            status_code=404,
            detail="Brief not found"
        )

    deleted_brief = {
        "id": brief.id,
        "title": brief.title,
        "description": brief.description
    }

    try:
        db.delete(brief)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Brief deleted successfully",
        "brief": deleted_brief
    }
# ---------------- CREATE A TASK UNDER A BRIEF ----------------

@app.post(
    "/briefs/{brief_id}/tasks",
    response_model=TaskResponse,
    status_code=201
)
def create_task(
    brief_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db)
):

    # Check whether the parent brief exists
    brief = db.get(models.BriefModel, brief_id)

    if brief is None:
        raise HTTPException(
            status_code=404,
            detail="Brief not found"
        )

    # Create the task
    new_task = models.TaskModel(
        title=task.title,
        description=task.description,
        brief_id=brief_id
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

    except Exception:
        db.rollback()
        raise

    return new_task
# ---------------- RETRIEVE ALL TASKS UNDER A BRIEF ----------------

@app.get(
    "/briefs/{brief_id}/tasks",
    response_model=list[TaskResponse]
)
def get_tasks(
    brief_id: int,
    db: Session = Depends(get_db)
):

    # Check whether the parent brief exists
    brief = db.get(models.BriefModel, brief_id)

    if brief is None:
        raise HTTPException(
            status_code=404,
            detail="Brief not found"
        )

    # Retrieve tasks belonging to this brief
    tasks = db.query(models.TaskModel).filter(
        models.TaskModel.brief_id == brief_id
    ).order_by(
        models.TaskModel.id
    ).all()

    return tasks
# ---------------- RETRIEVE ONE TASK ----------------

@app.get(
    "/briefs/{brief_id}/tasks/{task_id}",
    response_model=TaskResponse
)
def get_task(
    brief_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(models.TaskModel).filter(
        models.TaskModel.id == task_id,
        models.TaskModel.brief_id == brief_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task
# ---------------- UPDATE AN EXISTING TASK ----------------

@app.put(
    "/briefs/{brief_id}/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(
    brief_id: int,
    task_id: int,
    updated_data: TaskUpdate,
    db: Session = Depends(get_db)
):

    task = db.query(models.TaskModel).filter(
        models.TaskModel.id == task_id,
        models.TaskModel.brief_id == brief_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.title = updated_data.title
    task.description = updated_data.description
    task.status = updated_data.status

    try:
        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise

    return task
# ---------------- DELETE AN EXISTING TASK ----------------

@app.delete("/briefs/{brief_id}/tasks/{task_id}")
def delete_task(
    brief_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(models.TaskModel).filter(
        models.TaskModel.id == task_id,
        models.TaskModel.brief_id == brief_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    deleted_task = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "brief_id": task.brief_id
    }

    try:
        db.delete(task)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Task deleted successfully",
        "task": deleted_task
    }
