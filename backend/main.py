from fastapi import FastAPI

from database import engine, Base
import models

from routes.companies import router as company_router
from routes.drives import router as drive_router
from routes.messages import router as message_router
from routes.analytics import router as analytics_router
from routes.verifications import router as verification_router

app = FastAPI(
    title="Placement Intelligence and Feedback Analytics System",
    description="AI-powered placement intelligence system",
    version="1.0.0"
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Register API routes
app.include_router(company_router)
app.include_router(drive_router)
app.include_router(message_router)
app.include_router(analytics_router)
app.include_router(verification_router)

@app.get("/")
def root():

    return {
        "message": "Placement Intelligence System is running!"
    }


@app.get("/db-test")
def database_test():

    try:

        with engine.connect():

            return {
                "status": "success",
                "message": "FastAPI connected to PostgreSQL!"
            }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }