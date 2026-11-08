from app.utils.auth import create_access_token, decode_token, get_password_hash, verify_password


def test_password_hash_roundtrip():
    hashed = get_password_hash("analyst123")
    assert verify_password("analyst123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_access_token_roundtrip():
    token = create_access_token("analyst@bank.pk")
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "analyst@bank.pk"
