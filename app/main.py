from fastapi import FastAPI
from app.routers import auth, user, chat, message
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Messenger API",
    version="1.0.0",
    debug=True
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chat.router)
app.include_router(message.router)

@app.get("/")
async def root():
    return {"message": "Messenger API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)