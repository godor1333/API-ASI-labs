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
def get_investment_proposals(db: Session = Depends(get_db)):
    proposals = db.query(models.InvestmentProposal).all()
    return proposals

@router.get("/proposals/{proposal_id}", response_model=schemas.Proposal)
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(models.InvestmentProposal).filter(
        models.InvestmentProposal.id == proposal_id
    ).first()
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal

@router.get("/decisions")
def get_investment_decisions(db: Session = Depends(get_db)):
    # Возвращает карту принятых инвестиционных решений
    approved_proposals = db.query(models.InvestmentProposal).filter(
        models.InvestmentProposal.status == "approved"
    ).all()
    
    decisions_map = []
    for proposal in approved_proposals:
        decisions_map.append({
            "id": proposal.id,
            "title": proposal.title,
            "asset": proposal.asset_symbol,
            "amount": proposal.target_amount,
            "timestamp": proposal.created_at,
            "consensus_ratio": calculate_consensus_ratio(proposal.id, db)
        })
    
    return decisions_map

def calculate_consensus_ratio(proposal_id: int, db: Session):
    votes = db.query(models.Vote).filter(models.Vote.proposal_id == proposal_id).all()
    if not votes:
        return 0
    
    total_weight = sum(vote.weight for vote in votes)
    for_weight = sum(vote.weight for vote in votes if vote.vote_type == "for")
    
    return for_weight / total_weight if total_weight > 0 else 0