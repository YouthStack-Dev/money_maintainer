from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import current_user
from app.debts.models import Debt
from app.debts.schemas import DebtCreate, DebtUpdate, DebtResponse, DebtRepaymentCreate, DebtRepaymentResponse, DebtSummary
from app.debts.service import create_debt, repay_debt, list_repayments, summary
from app.users.models import User

router=APIRouter()

def get_debt(db,user_id,debt_id):
    item=db.scalar(select(Debt).where(Debt.id==debt_id,Debt.user_id==user_id))
    if not item: raise HTTPException(404,"Debt not found")
    return item

@router.get("",response_model=list[DebtResponse])
def list_debts(user:User=Depends(current_user),db:Session=Depends(get_db)):
    return db.scalars(select(Debt).where(Debt.user_id==user.id).order_by(Debt.id.desc())).all()

@router.post("",response_model=DebtResponse,status_code=status.HTTP_201_CREATED)
def create(payload:DebtCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    try:return create_debt(db,user.id,payload.model_dump())
    except ValueError as e: db.rollback(); raise HTTPException(400,str(e))

@router.get("/summary",response_model=DebtSummary)
def get_summary(user:User=Depends(current_user),db:Session=Depends(get_db)):
    r=summary(db,user.id); return DebtSummary(total_borrowed_outstanding=r[__import__("app.debts.models",fromlist=["DebtDirection"]).DebtDirection.BORROWED][0],total_lent_outstanding=r[__import__("app.debts.models",fromlist=["DebtDirection"]).DebtDirection.LENT][0],active_borrowed_count=r[__import__("app.debts.models",fromlist=["DebtDirection"]).DebtDirection.BORROWED][1],active_lent_count=r[__import__("app.debts.models",fromlist=["DebtDirection"]).DebtDirection.LENT][1])

@router.get("/{debt_id}",response_model=DebtResponse)
def get(debt_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)): return get_debt(db,user.id,debt_id)

@router.patch("/{debt_id}",response_model=DebtResponse)
def update(debt_id:int,payload:DebtUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    item=get_debt(db,user.id,debt_id); values=payload.model_dump(exclude_unset=True)
    if item.outstanding_amount>0 and values.get("status")==__import__("app.debts.models",fromlist=["DebtStatus"]).DebtStatus.SETTLED: raise HTTPException(400,"Use repayment to settle a debt")
    for k,v in values.items(): setattr(item,k,v)
    db.commit(); db.refresh(item); return item

@router.delete("/{debt_id}",response_model=DebtResponse)
def cancel(debt_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    item=get_debt(db,user.id,debt_id)
    if item.outstanding_amount>0: item.status=__import__("app.debts.models",fromlist=["DebtStatus"]).DebtStatus.CANCELLED
    db.commit(); db.refresh(item); return item

@router.get("/{debt_id}/repayments",response_model=list[DebtRepaymentResponse])
def repayments(debt_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    try:return list_repayments(db,user.id,debt_id)
    except ValueError as e: raise HTTPException(404,str(e))

@router.post("/{debt_id}/repayments",response_model=DebtRepaymentResponse,status_code=status.HTTP_201_CREATED)
def repay(debt_id:int,payload:DebtRepaymentCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    try:_,r,_=repay_debt(db,user.id,debt_id,payload.model_dump()); return r
    except ValueError as e: db.rollback(); raise HTTPException(400,str(e))
