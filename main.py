#for requirements pipreqs . --force
#committ at end
#SQL DB, FASTAPI, SQLmodel to communicate with DB
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session, select
from typing import List, Optional
from scraper import Bass

DATABASE_URL = "sqlite:///bass.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

app = FastAPI()

# API Routes
@app.get("/api/basses", response_model=List[Bass])
def get_all_basses(
    name: Optional[str] = None,
    pickup: Optional[str] = None,
    strings: Optional[int] = None,
    frets: Optional[int] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
):
    """Get all basses from the database, optionally filtered by features."""
    with Session(engine) as session:
        statement = select(Bass)

        if name:
            statement = statement.where(Bass.name.contains(name))
        if pickup:
            statement = statement.where(Bass.pickup.contains(pickup))
        if strings is not None:
            statement = statement.where(Bass.strings == strings)
        if frets is not None:
            statement = statement.where(Bass.frets == frets)
        if min_score is not None:
            statement = statement.where(Bass.score >= min_score)
        if max_score is not None:
            statement = statement.where(Bass.score <= max_score)

        basses = session.exec(statement).all()
        return basses

@app.get("/api/basses/{bass_id}", response_model=Bass)
def get_bass(bass_id: int):
    """Get a specific bass by ID."""
    with Session(engine) as session:
        bass = session.get(Bass, bass_id)
        return bass

@app.get("/api/basses/name/{name}", response_model=List[Bass])
def search_basses(name: str):
    """Search for basses by name."""
    with Session(engine) as session:
        basses = session.exec(select(Bass).where(Bass.name.contains(name))).all()
        return basses

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
