from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from web3 import Web3

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bee:hive123@localhost:5432/beehive")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Blockchain configuration
BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))

def get_web3():
    return w3

def init_db():
    """Initialize database with test data"""
    from . import models
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create test user if doesn't exist
        user = db.query(models.User).filter(models.User.id == 1).first()
        if not user:
            test_user = models.User(
                id=1,
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password",
                bee_rating=2.5,
                voting_weight=1.5
            )
            db.add(test_user)
            db.commit()
            
        # Create test proposals if none exist
        proposals = db.query(models.InvestmentProposal).all()
        if not proposals:
            test_proposals = [
                models.InvestmentProposal(
                    title="Tech Growth Fund",
                    description="Investment in emerging tech companies",
                    asset_symbol="TECH",
                    target_amount=50000,
                    proposer_id=1
                ),
                models.InvestmentProposal(
                    title="Green Energy Portfolio", 
                    description="Sustainable energy investments",
                    asset_symbol="GREEN",
                    target_amount=75000,
                    proposer_id=1
                )
            ]
            db.add_all(test_proposals)
            db.commit()
            
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()