from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    bee_rating = Column(Float, default=1.0)
    voting_weight = Column(Float, default=1.0)
    total_contribution = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    votes = relationship("Vote", back_populates="user")
    proposals = relationship("InvestmentProposal", back_populates="proposer")

class InvestmentProposal(Base):
    __tablename__ = "investment_proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    asset_symbol = Column(String(10))
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    proposer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="voting")  # voting, approved, rejected, funded
    consensus_threshold = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    proposer = relationship("User", back_populates="proposals")
    votes = relationship("Vote", back_populates="proposal")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    proposal_id = Column(Integer, ForeignKey("investment_proposals.id"))
    vote_type = Column(String(10))  # for, against
    weight = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="votes")
    proposal = relationship("InvestmentProposal", back_populates="votes")

class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    approval_count = Column(Integer, default=0)
    required_approvals = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApprovalVote(Base):
    __tablename__ = "approval_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    withdrawal_id = Column(Integer, ForeignKey("withdrawal_requests.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    approved = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)