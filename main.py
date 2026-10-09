from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db, engine
from app.models import Base, Question
from pydantic import BaseModel


class QuestionCreate(BaseModel):
    question: str
    answer: str
    category: str | None = None
    source: str | None = None


app = FastAPI(title="Questions API", version="1.0.0")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Questions API funcionando", "endpoints": ["/questions", "/questions/{id}"]}


@app.get("/questions")
def list_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions



@app.post("/questions", status_code=201)
def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db)
):
    new_question = Question(
        question=question_data.question,
        answer=question_data.answer,
        category=question_data.category,
        source=question_data.source
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return {
        "message": "Pregunta creada exitosamente",
        "question": new_question
    }


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):

    total_questions = db.query(Question).count()

    category_stats = (
        db.query(
            Question.category,
            func.count(Question.id)
        )
        .group_by(Question.category)
        .all()
    )

    by_category = {
        category: count
        for category, count in category_stats
    }

    return {
        "total_questions": total_questions,
        "by_category": by_category
    }



@app.get("/questions/category/{category}")
def get_questions_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    questions = (
        db.query(Question)
        .filter(Question.category == category)
        .all()
    )

    return questions

@app.get("/questions/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        return {"error": "Pregunta no encontrada"}
    return question

