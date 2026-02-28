# main.py
import os
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# =========================
# DB (PostgreSQL) 設定
# =========================
# App Service の Configuration で DATABASE_URL を設定してください
# 例: postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Set it in App Service Configuration.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# Model (SQLAlchemy)
# =========================
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)


# =========================
# Schema (Pydantic)
# =========================
class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ItemOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# App
# =========================
app = FastAPI()


@app.on_event("startup")
def on_startup():
    # 学習用：起動時にテーブル作成
    # 運用では Alembic 等のマイグレーション推奨
    Base.metadata.create_all(bind=engine)


# 疎通確認（DBにつながるか）
@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True}


# 追加（登録）
@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    item = Item(title=title, description=payload.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# 一覧（動作確認用）
@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).order_by(Item.id.desc()).all()


# 削除
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")

    db.delete(item)
    db.commit()
    return {"deleted": True, "id": item_id}