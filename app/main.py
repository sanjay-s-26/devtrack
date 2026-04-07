from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DevTrack API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "DevTrack API is running"}


# Wrap router imports in try/except blocks to prevent app crash if routers are missing

try:
    from app.routers import auth
    app.include_router(auth.router)
except ImportError:
    pass  # TODO: implement app/routers/auth.py

try:
    from app.routers import users
    app.include_router(users.router)
except ImportError:
    pass  # TODO: implement app/routers/users.py

try:
    from app.routers import projects
    app.include_router(projects.router)
except ImportError:
    pass  # TODO: implement app/routers/projects.py

try:
    from app.routers import issues
    app.include_router(issues.router)
except ImportError:
    pass  # TODO: implement app/routers/issues.py
