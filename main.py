from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routes import router as chat_router
from auth import router as auth_router


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://10.21.19.133",
    "http://192.168.155.230",
    "https://neora.netlify.app",
    "https://neora.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["auth"], prefix="/api/v1")
app.include_router(chat_router, tags=["chatbot"], prefix="/api/v1")
