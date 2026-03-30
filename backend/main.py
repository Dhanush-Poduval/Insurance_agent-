
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import logging
from datetime import datetime

# Import routers
from api.pricing_routes import router as pricing_router, trigger_router as pricing_trigger_router
from api.trigger_routes import router as trigger_router

# Import services for initialization
from services.payout_service import PayoutService, init_payout_service
from services.fraud_detection_service import FraudDetectionService, init_fraud_detection_service
from database import SessionLocal

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 646b16d872bbb75af685bb0402be6b9d2765b86c
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Insurance Pricing Engine",
    description="Real-time dynamic pricing for gig workers",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background scheduler
scheduler = BackgroundScheduler()

def check_triggers_scheduled():
    """Run trigger evaluation every 5 minutes"""
    logger.info("⏰ Running scheduled trigger check...")
    from services.trigger_service import trigger_engine
    asyncio.run(trigger_engine.evaluate_all_zones())

# Include routers
app.include_router(pricing_router)
app.include_router(pricing_trigger_router)
app.include_router(trigger_router)

# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Insurance Pricing Engine API",
        "version": "2.0.0",
        "docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scheduler_running": scheduler.running
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on app startup"""
    logger.info("🚀 Application starting up...")
    
    # Initialize database tables
    from database import Base, engine as db_engine
    Base.metadata.create_all(bind=db_engine)
    logger.info("✅ Database tables initialized")
    
    # Initialize services with database session
    db = SessionLocal()
    try:
        # Initialize payout service
        from services import payout_service as payout_module
        payout_module.payout_service = PayoutService(db)
        logger.info("✅ Payout service initialized")
        
        # Initialize fraud detection service
        from services import fraud_detection_service as fraud_module
        fraud_module.fraud_detection_service = FraudDetectionService(db)
        logger.info("✅ Fraud detection service initialized")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
    finally:
        db.close()
    
    # Start background scheduler
    scheduler.add_job(
        check_triggers_scheduled, 
        'interval', 
        minutes=5,
        id='trigger_checker'
    )
    scheduler.start()
    logger.info("✅ Trigger scheduler started (every 5 minutes)")
    
    logger.info("✅ All services initialized successfully!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    logger.info("🛑 Application shutting down...")
    scheduler.shutdown()
    logger.info("✅ Trigger scheduler stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
<<<<<<< HEAD
=======
@app.post('/risk_calculation')
def risk_calculation():
    pass
>>>>>>> main
=======
@app.post('/risk_calculation')
def risk_calculation():
    pass
>>>>>>> 646b16d872bbb75af685bb0402be6b9d2765b86c
