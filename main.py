from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated, Optional
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import auth
from auth import get_current_user



app = FastAPI(
    title="Todo API",
    description="A simple API to manage todo items",
    version="0.1.0"
)

app.include_router(auth.router)


# Creating Tables
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@app.get("/", tags=["welcome"], status_code=200)
def welcome():
    return {"message": "Welcome to the todo API"}


# Pydantic class to handle data validation
class TodoBase(BaseModel):
    title: str
    description: str
    completed: bool



# Adding New Todo    
@app.post("/todos")
def create_todo(todo: TodoBase, user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_todo = models.Todos(title = todo.title, description = todo.description, completed = todo.completed, user_id = user["id"])
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return {"message": "Todo created successfully"}

# Getting All Todos

@app.get("/todos")
def get_todos(db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")    
    todos = db.query(models.Todos).where(models.Todos.user_id == user["id"]).all()
    return todos


# Getting Single Todo via ID

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")    
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).where(models.Todos.user_id == user["id"]).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# Pydantic class for handling update
class UpdateTodosBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# Updating Todo via ID

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, db: db_dependency, user: user_dependency, todo: UpdateTodosBase):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_query = db.query(models.Todos).filter(models.Todos.id == todo_id).where(models.Todos.user_id == user["id"])
    todo_found = todo_query.first()
    if not todo_found:
        raise HTTPException(status_code=404, detail="Todo not found")
   
    if todo.title is not None:
        todo_found.title = todo.title
    if todo.description is not None:
        todo_found.description = todo.description
    if todo.completed is not None:
        todo_found.completed = todo.completed
    db.commit()
    db.refresh(todo_found)
    return {"message": "Todo updated successfully"}

# Deleting Todo Via ID

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, user: user_dependency,db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")    
    
    todo_query = db.query(models.Todos).filter(models.Todos.id == todo_id).where(models.Todos.user_id == user["id"])
    todo_found = todo_query.first()
    if not todo_found:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_query.delete()
    db.commit()
    return {"message": "Todo deleted successfully"}
