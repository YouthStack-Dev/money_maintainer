[object Object]
def test_merge_duplicate_transactions():
    result = parse_correction(
        "merge transaction 43 into transaction 42",
        date(2026, 9, 30),
    )
    assert result["action"] == CorrectionAction.MERGE
    assert result["duplicate_transaction_id"] == 43
    assert result["transaction_id"] == 42
    assert result["confidence"] == "HIGH"


def test_merge_same_transaction_needs_confirmation():
    result = parse_correction(
        "merge transaction 42 into transaction 42",
        date(2026, 9, 30),
    )
    assert "distinct_transactions" in result["missing"]
    assert result["confidence"] == "MEDIUM"


def test_merge_duplicate_transactions():
    result = parse_correction(
        "merge transaction 43 into transaction 42",
        date(2026, 9, 30),
    )
    assert result["action"] == CorrectionAction.MERGE
    assert result["duplicate_transaction_id"] == 43
    assert result["transaction_id"] == 42
    assert result["confidence"] == "HIGH"


def test_merge_same_transaction_needs_confirmation():
    result = parse_correction(
        "merge transaction 42 into transaction 42",
        date(2026, 9, 30),
    )
    assert "distinct_transactions" in result["missing"]
    assert result["confidence"] == "MEDIUM"
