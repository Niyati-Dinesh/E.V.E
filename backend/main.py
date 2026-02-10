# =============================================================================
# MAIN BACKEND FILE 
# START -  uvicorn main:app --reload  
# =============================================================================



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth

app = FastAPI(title="E.V.E Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,                  # REQUIRED for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
# Authentication router
app.include_router(auth.router)
# Task router

# health checkpoint
@app.get("/")
def root():
    return {"message": "E.V.E Backend is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}