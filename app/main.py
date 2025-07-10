from fastapi import FastAPI
from app.routes import url, report

app = FastAPI()
app.include_router(report.router)
app.include_router(url.router)
