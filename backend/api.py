from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sarvam CommunityOS API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI

from routes.tts import router as tts_router
from routes.stt import router as stt_router
from routes.analytics import router as analytics_router
from routes.contributors import router as contributors_router
from routes.knowledge import router as knowledge_router
from routes.documents import router as document_router
from routes.community import router as community_router
from routes.support import router as support_router
from routes.feedback import router as feedback_router
from routes.events import router as events_router
from routes.interactions import router as interactions_router

app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(analytics_router)
app.include_router(contributors_router)
app.include_router(knowledge_router)
app.include_router(document_router)
app.include_router(community_router)
app.include_router(support_router)
app.include_router(feedback_router)
app.include_router(events_router)
app.include_router(interactions_router)

# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "communityos",
    }