from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
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

@router.post("/request", response_model=schemas.WithdrawalRequest)
def create_withdrawal_request(request: schemas.WithdrawalRequestCreate, db: Session = Depends(get_db)):
    # Проверяем баланс пользователя
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if user.total_contribution < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Создаем запрос на вывод
    db_request = models.WithdrawalRequest(
        user_id=request.user_id,
        amount=request.amount,
        required_approvals=3  # Случайная выборка из 3 участников
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Выбираем случайных участников для подтверждения
    select_random_approvers(db_request.id, db)
    
    return db_request

@router.post("/approve/{request_id}")
def approve_withdrawal(request_id: int, approver_id: int, db: Session = Depends(get_db)):
    withdrawal_request = db.query(models.WithdrawalRequest).filter(
        models.WithdrawalRequest.id == request_id
    ).first()
    
    if withdrawal_request is None:
        raise HTTPException(status_code=404, detail="Withdrawal request not found")
    
    # Проверяем, может ли этот пользователь подтверждать
    can_approve = db.query(models.ApprovalVote).filter(
        models.ApprovalVote.withdrawal_id == request_id,
        models.ApprovalVote.approver_id == approver_id
    ).first()
    
    if not can_approve:
        raise HTTPException(status_code=403, detail="Not authorized to approve this request")
    
    # Записываем голос подтверждения
    approval_vote = models.ApprovalVote(
        withdrawal_id=request_id,
        approver_id=approver_id,
        approved=True
    )
    db.add(approval_vote)
    
    # Обновляем счетчик подтверждений
    withdrawal_request.approval_count += 1
    
    # Проверяем, достигнут ли необходимый порог
    if withdrawal_request.approval_count >= withdrawal_request.required_approvals:
        withdrawal_request.status = "approved"
        # Здесь будет вызов смарт-контракта для выполнения вывода средств
    
    db.commit()
    return {"message": "Withdrawal approved"}

def select_random_approvers(withdrawal_id: int, db: Session):
    # Выбираем случайных активных пользователей (кроме самого инициатора)
    withdrawal = db.query(models.WithdrawalRequest).filter(
        models.WithdrawalRequest.id == withdrawal_id
    ).first()
    
    all_users = db.query(models.User).filter(
        models.User.id != withdrawal.user_id,
        models.User.bee_rating >= 1.0  # Только пользователи с достаточным рейтингом
    ).all()
    
    # Выбираем случайную выборку
    approvers = random.sample(all_users, min(3, len(all_users)))
    
    # Создаем записи для голосования подтверждения
    for approver in approvers:
        approval_vote = models.ApprovalVote(
            withdrawal_id=withdrawal_id,
            approver_id=approver.id,
            approved=False
        )
        db.add(approval_vote)
    
    db.commit()

@router.get("/requests/{user_id}", response_model=List[schemas.WithdrawalRequest])
def get_user_withdrawal_requests(user_id: int, db: Session = Depends(get_db)):
    requests = db.query(models.WithdrawalRequest).filter(
        models.WithdrawalRequest.user_id == user_id
    ).all()
    return requests