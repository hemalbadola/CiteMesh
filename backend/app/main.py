from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .api import activity, chat, citations, collections, papers, pdf, search, users
from .db import engine
from .models import (
    CitationLink,
    Collection,
    CollectionPaper,
    MentorStudentLink,
    Profile,
    User,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown


app = FastAPI(title="CiteMesh Backend", version="0.1.0", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://citemesh.web.app",
        "https://citemesh.firebaseapp.com",
        "https://paperverse-kvw2y.ondigitalocean.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "message": "CiteMesh API is running"}


# Register API routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(activity.router, prefix="/api/activity", tags=["activity"])
app.include_router(collections.router, prefix="/api/collections", tags=["collections"])
app.include_router(citations.router, prefix="/api/citations", tags=["citations"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["pdf"])
