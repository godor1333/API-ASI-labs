from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    email: str
    bee_rating: float = 1.0
    voting_weight: float = 1.0

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    total_contribution: float = 0.0

    class Config:
        from_attributes = True

class ProposalBase(BaseModel):
    title: str
    description: str
    asset_symbol: str
    target_amount: float

class ProposalCreate(ProposalBase):
    proposer_id: int

class Proposal(ProposalBase):
    id: int
    proposer_id: int
    status: str
    current_amount: float = 0.0
    consensus_threshold: float = 0.7
    created_at: datetime

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    user_id: int
    proposal_id: int
    vote_type: str

class VoteCreate(VoteBase):
    pass

class Vote(VoteBase):
    id: int
    weight: float
    created_at: datetime

    class Config:
        from_attributes = True

class WithdrawalRequestBase(BaseModel):
    user_id: int
    amount: float

class WithdrawalRequestCreate(WithdrawalRequestBase):
    pass

class WithdrawalRequest(WithdrawalRequestBase):
    id: int
    status: str
    approval_count: int
    required_approvals: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None