from app.financial_relationships.parser import extract_person, infer_relationship
from app.financial_relationships.schemas import RelationshipIntent

def test_lending_is_relationship_not_expense():
    intent = infer_relationship("7000 lending to Giri")
    assert intent == RelationshipIntent.LEND
    assert extract_person("7000 lending to Giri", intent) == "Giri"

def test_borrowed_from_person():
    intent = infer_relationship("5000 borrowed from Sai")
    assert intent == RelationshipIntent.BORROW
    assert extract_person("5000 borrowed from Sai", intent) == "Sai"

def test_receive_repayment():
    text = "Giri paid me 3000"
    intent = infer_relationship(text)
    assert intent == RelationshipIntent.RECEIVE_LENT_REPAYMENT
    assert extract_person(text, intent) == "Giri"


def test_receive_repayment_in_phrase():
    text = "in sai minus 3500 he paid me"
    intent = infer_relationship(text)
    assert intent == RelationshipIntent.RECEIVE_LENT_REPAYMENT
    assert extract_person(text, intent) == "sai"

def test_credit_card_payment_is_transfer():
    assert infer_relationship("SBI CC 18999 paid") == RelationshipIntent.CREDIT_CARD_PAYMENT


def test_explicit_transfer_is_relationship():
    assert infer_relationship("5000 HDFC to cash") == RelationshipIntent.TRANSFER

def test_credit_card_purchase_is_expense():
    assert infer_relationship("450 petrol Axis CC") == RelationshipIntent.CREDIT_CARD_PURCHASE

def test_salary_refund_and_emi():
    assert infer_relationship("salary 29800") == RelationshipIntent.SALARY
    assert infer_relationship("refund 2000") == RelationshipIntent.REFUND
    assert infer_relationship("EMI 10753") == RelationshipIntent.EMI
