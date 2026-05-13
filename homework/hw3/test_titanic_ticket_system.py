import builtins
import contextlib
import io
import importlib.util
import sys
from pathlib import Path

import pandas as pd


SCRIPT_PATH = Path(__file__).with_name("titanic_ticket_system.py")
spec = importlib.util.spec_from_file_location("titanic_ticket_system", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def run_test(name, func):
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            func()
        print(f"[PASS] {name}")
    except AssertionError as e:
        print(f"[FAIL] {name}: {e}")
        out = stdout_buf.getvalue().strip()
        err = stderr_buf.getvalue().strip()
        if out:
            print(out)
        if err:
            print(err, file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] {name}: {type(e).__name__}: {e}")
        out = stdout_buf.getvalue().strip()
        err = stderr_buf.getvalue().strip()
        if out:
            print(out)
        if err:
            print(err, file=sys.stderr)


def mock_inputs(values):
    values = iter(values)

    def _mock_input(prompt=""):
        return next(values)

    return _mock_input


def test_load_data():
    df = module.load_data("titanic-2.csv")
    assert not df.empty, "Dataset should not be empty"
    required = {"pclass", "survived", "sex", "age", "ticket", "fare"}
    assert required.issubset(df.columns), "Missing required Titanic columns"


def test_get_fare_ranges_ignores_zero_and_missing():
    test_df = pd.DataFrame({
        "pclass": [1, 1, 1, 2, 2, 3, 3],
        "fare": [100, 0, None, 50, 80, 20, 150]
    })
    ranges = module.get_fare_ranges(test_df)
    assert ranges[1] == (100.0, 100.0), "Class 1 should ignore 0 and NaN fares"
    assert ranges[2] == (50.0, 80.0), "Class 2 min/max incorrect"
    assert ranges[3] == (20.0, 150.0), "Class 3 min/max incorrect"


def test_get_existing_tickets_returns_clean_strings():
    test_df = pd.DataFrame({"ticket": [" 12345 ", 67890, None]})
    tickets = module.get_existing_tickets(test_df)
    assert "12345" in tickets, "Ticket should be stripped"
    assert "67890" in tickets, "Numeric ticket should become string"
    assert None not in tickets, "None should not be included"


def test_get_valid_name_rejects_spaces_then_accepts_name():
    original_input = builtins.input
    builtins.input = mock_inputs(["   ", "---", "Az2", "John 2", "123hi", "  Alex Kuznetsov  "])
    try:
        result = module.get_valid_name()
        assert result == "Alex Kuznetsov", "Name should be stripped and validated"
    finally:
        builtins.input = original_input


def test_get_valid_age_rejects_invalid_then_accepts_valid():
    original_input = builtins.input
    builtins.input = mock_inputs(["abc", "-5", "131", "25"])
    try:
        result = module.get_valid_age()
        assert result == 25.0, "Age should accept valid numeric value in range"
    finally:
        builtins.input = original_input


def test_get_valid_sex_rejects_invalid_then_accepts_valid():
    original_input = builtins.input
    builtins.input = mock_inputs(["unknown", " Male "])
    try:
        result = module.get_valid_sex()
        assert result == "male", "Sex should be normalized to lowercase and validated"
    finally:
        builtins.input = original_input


def test_get_valid_fare_rejects_invalid_then_accepts_float():
    original_input = builtins.input
    builtins.input = mock_inputs(["abc", "175.5"])
    try:
        result = module.get_valid_fare()
        assert result == 175.5, "Fare should accept valid float"
    finally:
        builtins.input = original_input


def test_classify_fare_to_class_prefers_best_class_on_overlap():
    fare_ranges = {1: (100, 300), 2: (50, 200), 3: (20, 150)}
    result = module.classify_fare_to_class(140, fare_ranges)
    assert result == 1, "Overlap should promote passenger to best class"


def test_classify_fare_to_class_exact_single_match():
    fare_ranges = {1: (100, 300), 2: (50, 90), 3: (20, 40)}
    result = module.classify_fare_to_class(75, fare_ranges)
    assert result == 2, "Fare 75 should map to class 2 only"


def test_classify_fare_to_class_fallback_to_closest_range():
    fare_ranges = {1: (100, 300), 2: (50, 80), 3: (20, 40)}
    result = module.classify_fare_to_class(85, fare_ranges)
    assert result == 2, "Unmatched fare should map to closest class range"


def test_generate_unique_ticket_returns_6_digits_and_unique():
    existing = {"123456", "654321"}
    ticket = module.generate_unique_ticket(existing)
    assert len(ticket) == 6, "Ticket should be exactly 6 digits"
    assert ticket.isdigit(), "Ticket should contain only digits"
    assert ticket in existing, "Generated ticket should be added to set"
    assert ticket not in {"123456", "654321"}, "Generated ticket must be unique"


def test_calculate_survival_exact_group_match():
    test_df = pd.DataFrame({
        "pclass": [1, 1, 1, 2],
        "sex": ["female", "female", "male", "female"],
        "age": [30, 35, 30, 30],
        "survived": [1, 1, 0, 0]
    })
    survival, death = module.calculate_survival(test_df, 1, "female", 30)
    assert survival == 100.0, "Exact subgroup should return 100% survival here"
    assert death == 0.0, "Death should be inverse of survival"


def test_calculate_survival_fallback_to_class_and_sex():
    test_df = pd.DataFrame({
        "pclass": [1, 1, 1],
        "sex": ["male", "male", "female"],
        "age": [30, 40, 10],
        "survived": [1, 0, 1]
    })
    survival, death = module.calculate_survival(test_df, 1, "male", 10)
    assert survival == 50.0, "Should fallback to pclass + sex when exact age group missing"
    assert death == 50.0, "Death should be inverse of survival"


def test_calculate_survival_fallback_to_class_only():
    test_df = pd.DataFrame({
        "pclass": [2, 2, 2],
        "sex": ["female", "female", "female"],
        "age": [30, 40, 50],
        "survived": [1, 0, 1]
    })
    survival, death = module.calculate_survival(test_df, 2, "male", 12)
    assert survival == 66.7, "Should fallback to class only when sex subgroup missing"
    assert death == 33.3, "Death should be inverse of survival"


def test_save_ticket_creates_expected_format():
    output_file = Path("test_passenger_ticket.txt")
    if output_file.exists():
        output_file.unlink()

    module.save_ticket("111111", 175.0, 76.0, 1, "male", "Alex Kuznetsov", output_file)
    text = output_file.read_text(encoding="utf-8")

    assert "ticket: 111111 | fare: 175" in text, "Ticket line format is wrong"
    assert "age: 76        | class: 1" in text, "Age/class line format is wrong"
    assert "sex: male      | name: Alex Kuznetsov" in text, "Sex/name line format is wrong"

    output_file.unlink()


def main():
    tests = [
        ("load_data", test_load_data),
        ("get_fare_ranges ignores zero and missing", test_get_fare_ranges_ignores_zero_and_missing),
        ("get_existing_tickets returns clean strings", test_get_existing_tickets_returns_clean_strings),
        ("get_valid_name rejects spaces then accepts valid", test_get_valid_name_rejects_spaces_then_accepts_name),
        ("get_valid_age rejects invalid then accepts valid", test_get_valid_age_rejects_invalid_then_accepts_valid),
        ("get_valid_sex rejects invalid then accepts valid", test_get_valid_sex_rejects_invalid_then_accepts_valid),
        ("get_valid_fare rejects invalid then accepts float", test_get_valid_fare_rejects_invalid_then_accepts_float),
        ("classify_fare_to_class overlap promotion", test_classify_fare_to_class_prefers_best_class_on_overlap),
        ("classify_fare_to_class exact single match", test_classify_fare_to_class_exact_single_match),
        ("classify_fare_to_class fallback closest", test_classify_fare_to_class_fallback_to_closest_range),
        ("generate_unique_ticket uniqueness", test_generate_unique_ticket_returns_6_digits_and_unique),
        ("calculate_survival exact group", test_calculate_survival_exact_group_match),
        ("calculate_survival fallback class+sex", test_calculate_survival_fallback_to_class_and_sex),
        ("calculate_survival fallback class only", test_calculate_survival_fallback_to_class_only),
        ("save_ticket expected format", test_save_ticket_creates_expected_format),
    ]

    for name, func in tests:
        run_test(name, func)


if __name__ == "__main__":
    main()