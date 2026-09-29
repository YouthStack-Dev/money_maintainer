from app.core.security import hash_password,verify_password,token_hash

def test_password_hash():
    h=hash_password("StrongPassword123!")
    assert h!="StrongPassword123!"
    assert verify_password("StrongPassword123!",h)
    assert not verify_password("wrong",h)

def test_token_hash():
    assert token_hash("abc")==token_hash("abc")
    assert token_hash("abc")!=token_hash("xyz")
