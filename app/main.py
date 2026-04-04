from fastapi import FastAPI
from app.routers import auth, user, chat, message

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