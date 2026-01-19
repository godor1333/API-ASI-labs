from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, w3, init_db
from . import models
from .routers import users, voting, investments, withdrawals

# Initialize database with test data
init_db()

# ... остальной код без изменений
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BeeHive Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(voting.router, prefix="/api/voting", tags=["voting"])
app.include_router(investments.router, prefix="/api/investments", tags=["investments"])
app.include_router(withdrawals.router, prefix="/api/withdrawals", tags=["withdrawals"])

@app.get("/")
async def root():
    return {"message": "BeeHive Decentralized Investment Platform"}

@app.get("/health")
async def health_check():
    blockchain_status = "connected" if w3.is_connected() else "disconnected"
    return {
        "status": "healthy", 
        "service": "beehive-backend",
        "blockchain": blockchain_status,
        "block_number": w3.eth.block_number if w3.is_connected() else None
    }

@app.get("/blockchain/accounts")
async def get_blockchain_accounts():
    from .blockchain_service import blockchain_service
    accounts = blockchain_service.get_accounts()
    balances = {account: float(blockchain_service.get_balance(account)) for account in accounts}
    return {
        "accounts": accounts,
        "balances": balances,
        "connected": w3.is_connected()
    }