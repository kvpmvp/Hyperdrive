from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import projects, contributions, webhooks, sync

app = FastAPI(title=settings.app_name)

# Debug: print out the request origins that will be allowed
print("✅ Loaded CORS origins:", settings.cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # local dev
    allow_origin_regex=r"https://.*\.app\.github\.dev",  # allow all Codespaces subdomains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(projects.router, prefix=settings.api_prefix)
app.include_router(contributions.router, prefix=settings.api_prefix)
app.include_router(webhooks.router, prefix=settings.api_prefix)
app.include_router(sync.router, prefix=settings.api_prefix)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Hyperdrive API is running"}
