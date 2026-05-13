import builtins
import contextlib
import io
import importlib.util
import math
import sys
from pathlib import Path

import pandas as pd


SCRIPT_PATH = Path(__file__).with_name("titanic_final_project.py")
spec = importlib.util.spec_from_file_location("titanic_final_project", SCRIPT_PATH)
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


def test_validate_titanic_schema_missing_columns_raises():
    df = pd.DataFrame({"pclass": [1], "fare": [10]})
    try:
        module.validate_titanic_schema(df)
        raise AssertionError("Expected ValueError for missing columns")
    except ValueError as e:
        msg = str(e).lower()
        assert "missing" in msg and "required" in msg, "Error message should mention missing required columns"


def test_get_global_fare_limits_ignores_zero_and_nan():
    df = pd.DataFrame({"fare": [0, None, 10, 20.5, 0]})
    lo, hi = module.get_global_fare_limits(df)
    assert lo == 10.0, "Global min fare should ignore 0/NaN"
    assert hi == 20.5, "Global max fare should ignore 0/NaN"


def test_get_global_fare_limits_all_invalid_raises():
    df = pd.DataFrame({"fare": [0, 0, None, float("nan")]})
    try:
        module.get_global_fare_limits(df)
        raise AssertionError("Expected ValueError when no valid positive fares")
    except ValueError:
        pass


def test_get_fare_ranges_ignores_zero_and_missing_and_is_numeric():
    df = pd.DataFrame(
        {
            "pclass": [1, 1, 2, 2, 3, 3, 3, None],
            "fare": [100, 0, 50, None, 20, 150, "200", 999],
        }
    )
    ranges = module.get_fare_ranges(df)
    assert ranges[1] == (100.0, 100.0)
    assert ranges[2] == (50.0, 50.0)
    assert ranges[3] == (20.0, 200.0)


def test_get_existing_tickets_returns_clean_strings():
    df = pd.DataFrame({"ticket": [" 12345 ", 67890, None]})
    tickets = module.get_existing_tickets(df)
    assert "12345" in tickets
    assert "67890" in tickets
    assert None not in tickets


def test_get_valid_name_rejects_spaces_and_symbols_then_accepts_name():
    original_input = builtins.input
    builtins.input = mock_inputs(["   ", "---", "Az2", "John 2", "123hi", "  Alex Kuznetsov  "])
    try:
        result = module.get_valid_name()
        assert result == "Alex Kuznetsov"
    finally:
        builtins.input = original_input


def test_get_valid_fare_reprompts_until_legal_range():
    original_input = builtins.input
    # invalid text -> out of range -> valid
    builtins.input = mock_inputs(["abc", "999", "50"])
    try:
        fare = module.get_valid_fare(10, 100)
        assert fare == 50.0
    finally:
        builtins.input = original_input


def test_get_valid_fare_rejects_nan_and_inf():
    original_input = builtins.input
    builtins.input = mock_inputs(["nan", "inf", "20"])
    try:
        fare = module.get_valid_fare(10, 100)
        assert fare == 20.0
        assert math.isfinite(fare)
    finally:
        builtins.input = original_input


def test_classify_fare_to_class_prefers_best_class_on_overlap():
    fare_ranges = {1: (100, 300), 2: (50, 200), 3: (20, 150)}
    result = module.classify_fare_to_class(140, fare_ranges)
    assert result == 1, "Overlap should promote passenger to best (smallest) class"


def test_classify_fare_to_class_fallback_to_closest_range():
    fare_ranges = {1: (100, 300), 2: (50, 80), 3: (20, 40)}
    result = module.classify_fare_to_class(85, fare_ranges)
    assert result == 2, "Unmatched fare should map to closest class range"


def test_classify_fare_to_class_empty_ranges_raises():
    try:
        module.classify_fare_to_class(100, {})
        raise AssertionError("Expected ValueError for empty fare_ranges")
    except ValueError:
        pass


def test_calculate_survival_exact_group_match():
    df = pd.DataFrame(
        {
            "pclass": [1, 1, 1, 2],
            "sex": ["female", "female", "male", "female"],
            "age": [30, 35, 30, 30],
            "survived": [1, 1, 0, 0],
        }
    )
    survival, death = module.calculate_survival(df, 1, "female", 30)
    assert survival == 100.0
    assert death == 0.0


def test_calculate_survival_groupby_and_fallback_order():
    # level 1 missing (no under18 rows for class=1 male)
    # level 2 exists (class=1 male rows)
    df = pd.DataFrame(
        {
            "pclass": [1, 1, 1, 2],
            "sex": ["male", "male", "female", "male"],
            "age": [30, 40, 10, 30],
            "survived": [1, 0, 1, 0],
        }
    )
    survival, death = module.calculate_survival(df, 1, "male", 10)
    assert survival == 50.0, "Should fallback to pclass + sex when age_group subgroup missing"
    assert death == 50.0


def test_calculate_survival_fallback_to_class_only_then_overall():
    # No matching sex for class 2; should fallback to class-only.
    df = pd.DataFrame(
        {
            "pclass": [2, 2, 2],
            "sex": ["female", "female", "female"],
            "age": [30, 40, 50],
            "survived": [1, 0, 1],
        }
    )
    survival, death = module.calculate_survival(df, 2, "male", 12)
    assert survival == 66.7
    assert death == 33.3

    # Empty/invalid survived values -> final fallback returns (0, 100)
    df2 = pd.DataFrame(
        {
            "pclass": [1, 1],
            "sex": ["male", "female"],
            "age": [20, 30],
            "survived": [None, None],
        }
    )
    survival2, death2 = module.calculate_survival(df2, 1, "male", 20)
    assert survival2 == 0.0
    assert death2 == 100.0


def test_save_ticket_writes_required_format():
    output_file = Path(__file__).with_name("_tmp_passenger_ticket.txt")
    if output_file.exists():
        output_file.unlink()

    try:
        module.save_ticket("111111", 175.0, 76.0, 1, "male", "Alex Kuznetsov", output_file)
        text = output_file.read_text(encoding="utf-8")

        assert "--------------------------------------------------" in text
        assert "| ticket: 111111" in text
        assert "|  fare: 175" in text
        assert "| age: 76" in text
        assert "|  class: 1" in text
        assert "| sex: male" in text
        assert "|  name: Alex Kuznetsov" in text
    finally:
        if output_file.exists():
            output_file.unlink()


def main():
    tests = [
        ("validate_titanic_schema missing columns", test_validate_titanic_schema_missing_columns_raises),
        ("get_global_fare_limits ignores 0/NaN", test_get_global_fare_limits_ignores_zero_and_nan),
        ("get_global_fare_limits all invalid raises", test_get_global_fare_limits_all_invalid_raises),
        ("get_fare_ranges ignores 0/missing", test_get_fare_ranges_ignores_zero_and_missing_and_is_numeric),
        ("get_existing_tickets cleaned strings", test_get_existing_tickets_returns_clean_strings),
        ("get_valid_name rejects invalid", test_get_valid_name_rejects_spaces_and_symbols_then_accepts_name),
        ("get_valid_fare loops until legal", test_get_valid_fare_reprompts_until_legal_range),
        ("get_valid_fare rejects nan/inf", test_get_valid_fare_rejects_nan_and_inf),
        ("classify overlap promotion", test_classify_fare_to_class_prefers_best_class_on_overlap),
        ("classify fallback closest", test_classify_fare_to_class_fallback_to_closest_range),
        ("classify empty ranges raises", test_classify_fare_to_class_empty_ranges_raises),
        ("calculate_survival exact group", test_calculate_survival_exact_group_match),
        ("calculate_survival fallback order", test_calculate_survival_groupby_and_fallback_order),
        ("calculate_survival deeper fallbacks", test_calculate_survival_fallback_to_class_only_then_overall),
        ("save_ticket format", test_save_ticket_writes_required_format),
    ]

    for name, func in tests:
        run_test(name, func)


if __name__ == "__main__":
    main()
