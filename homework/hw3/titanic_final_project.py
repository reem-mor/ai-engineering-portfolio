"""Titanic ticket booking system (final project).

Flow summary:
- Load Titanic dataset
- Validate required columns
- Compute global fare limits and per-class fare ranges (ignore 0 / missing)
- Collect user input with validation
- Classify passenger into the best class based on fare ranges (promotion on overlap)
- Generate a unique 6-digit ticket number
- Save a formatted passenger ticket to a text file
- Estimate survival/death probability using pclass + sex + age_group (under18/over18)
"""

import random
import math
import sys
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

# Centralized file names make the script easier to update later.
CSV_FILE = BASE_DIR / "titanic.csv"
TICKET_OUTPUT_FILE = BASE_DIR / "passenger_ticket.txt"

REQUIRED_COLUMNS = {"pclass", "survived", "sex", "age", "ticket", "fare"}


def load_data(filepath: str | Path = CSV_FILE) -> pd.DataFrame:
    """Load the Titanic dataset from CSV.

    Uses an absolute path by default so the script runs from any working directory.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Titanic dataset not found: {path}")
    return pd.read_csv(path)


def validate_titanic_schema(df: pd.DataFrame) -> None:
    """Validate that the dataset contains the columns required by this project."""
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(
            "Titanic dataset is missing required columns: " + ", ".join(missing)
        )


def get_global_fare_limits(df: pd.DataFrame) -> tuple[float, float]:
    """Return global (min, max) fare paid, ignoring zeros and missing values."""
    fare = pd.to_numeric(df["fare"], errors="coerce")
    fare = fare[fare.notna() & (fare > 0)]
    if fare.empty:
        raise ValueError("Dataset has no valid positive fares to validate against.")
    return float(fare.min()), float(fare.max())


def get_fare_ranges(df: pd.DataFrame) -> dict[int, tuple[float, float]]:
    """
    Return min/max fare per class, ignoring zero and missing fares.

    Teacher logic:
    - Missing fares are not useful for range calculation.
    - Zero fares should also be ignored.
    """
    fare_df = df[["pclass", "fare"]].copy()

    # Convert columns safely to numeric. Invalid values become NaN.
    fare_df["fare"] = pd.to_numeric(fare_df["fare"], errors="coerce")
    fare_df["pclass"] = pd.to_numeric(fare_df["pclass"], errors="coerce")

    # Keep only real positive fares for class-range analysis.
    fare_df = fare_df[fare_df["fare"].notna() & (fare_df["fare"] > 0)].copy()
    fare_df = fare_df[fare_df["pclass"].notna()].copy()

    fare_ranges: dict[int, tuple[float, float]] = {}

    # Build a dictionary like:
    # {1: (min_fare, max_fare), 2: (...), 3: (...)}
    for pclass in sorted(fare_df["pclass"].unique()):
        class_fares = fare_df.loc[fare_df["pclass"] == pclass, "fare"].dropna()
        if class_fares.empty:
            continue
        fare_ranges[int(pclass)] = (float(class_fares.min()), float(class_fares.max()))

    if not fare_ranges:
        raise ValueError("Could not compute class fare ranges (no valid fares found).")

    return fare_ranges


def get_existing_tickets(df: pd.DataFrame) -> set[str]:
    """
    Return all existing ticket values as cleaned strings.

    Using a set gives fast membership checking when generating
    a new unique 6-digit ticket number.
    """
    if "ticket" not in df.columns:
        return set()
    return set(df["ticket"].dropna().astype(str).str.strip())


NAME_ALLOWED_SEPARATORS = set(" -'")


def is_valid_name(name: str) -> bool:
    name = name.strip()
    if not name:
        return False
    if any(ch.isdigit() for ch in name):
        return False
    if not any(ch.isalpha() for ch in name):
        return False
    if not all(ch.isalpha() or ch in NAME_ALLOWED_SEPARATORS for ch in name):
        return False
    return True


def get_valid_name() -> str:
    """
    Ask for passenger name until a valid non-empty string is entered.

    strip() removes spaces at the beginning and end.
    """
    while True:
        name = input("Enter passenger name: ").strip()

        if is_valid_name(name):
            return name

        print("Name is invalid. Use letters only (spaces/-/'). No digits.")


def get_valid_age() -> float:
    """
    Ask for passenger age until a valid numeric age is entered.

    Valid range: 0 to 130 inclusive.
    """
    while True:
        raw_age = input("Enter passenger age: ").strip()
        try:
            age = float(raw_age)

            if not math.isfinite(age):
                raise ValueError

            if 0 <= age <= 130:
                return age

            print("Age is wrong. Please enter age between 0 and 130.")
        except ValueError:
            print("Age must be a number. Please try again.")


def get_valid_sex() -> str:
    """
    Ask for passenger sex until the value is exactly male or female.

    lower() allows inputs like 'Male' or 'FEMALE' to still work.
    """
    while True:
        sex = input("Enter passenger sex (male/female): ").strip().lower()

        if sex in {"male", "female"}:
            return sex

        print("Sex value is illegal. Please enter male or female.")


def get_valid_fare(global_min: float, global_max: float) -> float:
    """
    Ask for passenger fare until a valid float is entered and within
    the dataset's global min/max fare range.
    """
    while True:
        raw_fare = input(
            f"Enter passenger fare (${global_min:g} - ${global_max:g}): "
        ).strip()
        try:
            fare = float(raw_fare)
        except ValueError:
            print("Fare must be a float number. Please try again.")
            continue

        if not math.isfinite(fare):
            print("Fare must be a float number. Please try again.")
            continue

        if global_min <= fare <= global_max:
            return fare

        print("Your fare payment is illegal. Please pay again.")


def classify_fare_to_class(
    fare: float,
    fare_ranges: dict[int, tuple[float, float]],
) -> int:
    """
    Assign the best class for a given fare.

    Rule:
    - If a fare fits multiple class ranges, choose the best class.
    - On Titanic, Class 1 is better than 2, and 2 is better than 3.
    - Therefore, if multiple matches exist, return the smallest class number.
    """
    if not fare_ranges:
        raise ValueError("Cannot classify fare because fare ranges are empty.")

    matching_classes = [
        pclass
        for pclass, (min_fare, max_fare) in fare_ranges.items()
        if min_fare <= fare <= max_fare
    ]

    # Overlap case: for example, if fare matches classes 1, 2, and 3,
    # we promote the passenger to the best class.
    if matching_classes:
        return min(matching_classes)

    # Fallback:
    # If the fare does not fit any exact range, assign the closest class
    # based on the nearest range boundary.
    closest_class = min(
        fare_ranges,
        key=lambda pclass: min(
            abs(fare - fare_ranges[pclass][0]), abs(fare - fare_ranges[pclass][1])
        ),
    )
    return closest_class


def generate_unique_ticket(existing_tickets: set[str]) -> str:
    """
    Generate a unique 6-digit ticket number.

    If the number already exists, keep generating until a new one is found.
    """
    while True:
        ticket_no = str(random.randint(100000, 999999))

        if ticket_no not in existing_tickets:
            # Add immediately so the same session cannot generate it again.
            existing_tickets.add(ticket_no)
            return ticket_no


def calculate_survival(
    df: pd.DataFrame, pclass: int, sex: str, age: float
) -> tuple[float, float]:
    """
    Return survival and death percentages using:
    pclass + sex + age_group

    Age groups:
    - under18
    - over18

    Fallback order:
    1. pclass + sex + age_group
    2. pclass + sex
    3. pclass
    4. overall dataset survival
    """
    work = df[["pclass", "sex", "age", "survived"]].copy()

    # Normalize and coerce types so grouping and lookups are reliable.
    work["pclass"] = pd.to_numeric(work["pclass"], errors="coerce")
    work["sex"] = work["sex"].astype(str).str.strip().str.lower()
    work["age"] = pd.to_numeric(work["age"], errors="coerce")
    work["survived"] = pd.to_numeric(work["survived"], errors="coerce")

    # Keep only rows that can contribute to survival statistics.
    work = work[work["survived"].notna()].copy()
    work = work[work["pclass"].notna()].copy()
    work = work[work["pclass"].isin([1, 2, 3, 1.0, 2.0, 3.0])].copy()
    work["pclass"] = work["pclass"].astype(int)

    # Build age groups as required (under18 / over18).
    # Missing ages are excluded from the age-group level and will be handled
    # by broader fallbacks.
    work["age_group"] = work["age"].apply(
        lambda x: (
            "under18" if pd.notna(x) and x < 18 else ("over18" if pd.notna(x) else None)
        )
    )

    normalized_sex = sex.strip().lower()
    passenger_age_group = "under18" if age < 18 else "over18"

    def _from_mean(mean_value: float | None) -> tuple[float, float] | None:
        if mean_value is None or pd.isna(mean_value):
            return None
        survival_pct = round(float(mean_value) * 100, 1)
        return survival_pct, round(100 - survival_pct, 1)

    # 1) pclass + sex + age_group (only rows with a known age_group)
    level_1 = (
        work.dropna(subset=["age_group"])
        .groupby(["pclass", "sex", "age_group"], dropna=True)["survived"]
        .mean()
    )
    key_1 = (pclass, normalized_sex, passenger_age_group)
    if key_1 in level_1.index:
        result = _from_mean(level_1.loc[key_1])
        if result is not None:
            return result

    # 2) pclass + sex
    level_2 = work.groupby(["pclass", "sex"], dropna=True)["survived"].mean()
    key_2 = (pclass, normalized_sex)
    if key_2 in level_2.index:
        result = _from_mean(level_2.loc[key_2])
        if result is not None:
            return result

    # 3) pclass
    level_3 = work.groupby(["pclass"], dropna=True)["survived"].mean()
    if pclass in level_3.index:
        result = _from_mean(level_3.loc[pclass])
        if result is not None:
            return result

    # 4) overall
    return _from_mean(work["survived"].mean()) or (0.0, 100.0)


def save_ticket(
    ticket_no: str,
    fare: float,
    age: float,
    pclass: int,
    sex: str,
    name: str,
    output_path: str | Path = TICKET_OUTPUT_FILE,
) -> None:
    """
    Save the passenger ticket in the required text format.
    """

    # Required ticket layout:
    # --------------------------------------------------
    # | ticket: 111111          |  fare: 175           |
    # --------------------------------------------------
    # | age: 76                 |  class: 1            |
    # --------------------------------------------------
    # | sex: male               |  name: Alex Kuznetsov|
    # --------------------------------------------------
    line = "-" * 50

    def row(left: str, right: str) -> str:
        # Total width is 50 chars.
        # | {left:<24} | {right:<19} |
        return f"| {left:<24} | {right:<19} |"

    ticket_text = "\n".join(
        [
            line,
            row(f"ticket: {ticket_no}", f" fare: {fare:g}"),
            line,
            row(f"age: {age:g}", f" class: {pclass}"),
            line,
            row(f"sex: {sex}", f" name: {name}"),
            line,
        ]
    )

    Path(output_path).write_text(ticket_text, encoding="utf-8")


def main() -> None:
    """
    Run the full passenger registration flow:
    1. Load Titanic data
    2. Prepare fare ranges and existing tickets
    3. Get valid user input
    4. Classify passenger
    5. Generate a unique ticket
    6. Save ticket to file
    7. Print death probability message
    """
    try:
        # Avoid Windows console encoding issues when printing Unicode characters.
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

        df = load_data()
        validate_titanic_schema(df)

        global_min, global_max = get_global_fare_limits(df)
        fare_ranges = get_fare_ranges(df)
        existing_tickets = get_existing_tickets(df)

        name = get_valid_name()
        age = get_valid_age()
        sex = get_valid_sex()
        fare = get_valid_fare(global_min, global_max)

        pclass = classify_fare_to_class(fare, fare_ranges)
        ticket_no = generate_unique_ticket(existing_tickets)

        save_ticket(ticket_no, fare, age, pclass, sex, name, TICKET_OUTPUT_FILE)

        _survival_pct, death_pct = calculate_survival(df, pclass, sex, age)
        first_name = name.split()[0]

        print("\n" + "=" * 55)
        print("Passenger registered successfully.")
        print(f"Assigned class: {pclass}")
        print(f"New ticket number: {ticket_no}")
        print(f"Ticket saved to '{TICKET_OUTPUT_FILE.name}'")
        print(f"\nDear {first_name}, your chances to die on our trip are {death_pct}%.")
        print("Enjoy your trip ☺")
        print("=" * 55)
    except Exception as exc:
        # Friendly CLI message (so the user doesn't get a long stack trace).
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
