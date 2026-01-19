from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/proposals", response_model=List[schemas.Proposal])
def get_proposals(db: Session = Depends(get_db)):
    try:
        proposals = db.query(models.InvestmentProposal).all()
        return proposals
    except Exception as e:
        # Return empty array if there's an error
        return []

@router.post("/proposals", response_model=schemas.Proposal)
def create_proposal(proposal: schemas.ProposalCreate, db: Session = Depends(get_db)):
    try:
        db_proposal = models.InvestmentProposal(
            title=proposal.title,
            description=proposal.description,
            asset_symbol=proposal.asset_symbol,
            target_amount=proposal.target_amount,
            proposer_id=proposal.proposer_id
        )
        db.add(db_proposal)
        db.commit()
        db.refresh(db_proposal)
        return db_proposal
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vote")
def cast_vote(vote: schemas.VoteCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already voted
        existing_vote = db.query(models.Vote).filter(
            models.Vote.user_id == vote.user_id,
            models.Vote.proposal_id == vote.proposal_id
        ).first()
        
        if existing_vote:
            raise HTTPException(status_code=400, detail="User already voted")
        
        # Get user voting weight
        user = db.query(models.User).filter(models.User.id == vote.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_vote = models.Vote(
            user_id=vote.user_id,
            proposal_id=vote.proposal_id,
            vote_type=vote.vote_type,
            weight=user.voting_weight
        )
        db.add(db_vote)
        db.commit()
        
        return {"message": "Vote cast successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))