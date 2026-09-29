from datetime import date
from decimal import Decimal
from uuid import uuid4
import pytest
from app.debts.models import DebtDirection, DebtStatus
from app.debts.service import create_debt, repay_debt
from app.accounts.models import Account
from app.core.database import SessionLocal
from app.users.models import User

@pytest.fixture
def data():
 db=SessionLocal(); u=User(email=f"d-{uuid4()}@x.test",full_name="Debt",password_hash="x"); db.add(u); db.flush()
 a=Account(user_id=u.id,name="Bank",account_type="BANK_ACCOUNT"); db.add(a); db.commit(); db.refresh(u); db.refresh(a)
 yield db,u,a
 db.rollback(); db.delete(u); db.commit(); db.close()

@pytest.mark.parametrize("direction,tx_type",[(DebtDirection.BORROWED,"EXPENSE"),(DebtDirection.LENT,"INCOME")])
def test_repayment_updates_balance_and_creates_transaction(data,direction,tx_type):
 db,u,a=data; d=create_debt(db,u.id,{"direction":direction,"person_name":"Alex","description":None,"original_amount":Decimal("1000"),"due_date":None})
 d,r,tx=repay_debt(db,u.id,d.id,{"account_id":a.id,"amount":Decimal("400"),"repayment_date":date(2026,9,29),"note":"partial"})
 assert d.outstanding_amount==Decimal("600.00"); assert d.status==DebtStatus.PARTIALLY_PAID; assert tx.transaction_type.value==tx_type
 d,r,tx=repay_debt(db,u.id,d.id,{"account_id":a.id,"amount":Decimal("600"),"repayment_date":date(2026,10,1),"note":"final"})
 assert d.outstanding_amount==0; assert d.status==DebtStatus.SETTLED

def test_repayment_cannot_exceed_balance(data):
 db,u,a=data; d=create_debt(db,u.id,{"direction":DebtDirection.BORROWED,"person_name":"Alex","description":None,"original_amount":Decimal("100"),"due_date":None})
 with pytest.raises(ValueError): repay_debt(db,u.id,d.id,{"account_id":a.id,"amount":Decimal("101"),"repayment_date":date(2026,9,29),"note":None})
