import pandas as pd
import random
import os

# ══════════════════════════════════════════════════════════════════
#  🚢  TITANIC TICKET BOOKING SYSTEM
#  Project 2 — Professional Python Solution
# ══════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────
# STEP 1: LOAD DATA
# ─────────────────────────────────────────────────────
def load_data(filepath="titanic.csv"):
    """Load Titanic dataset and return a DataFrame."""
    df = pd.read_csv(filepath)
    return df


# ─────────────────────────────────────────────────────
# STEP 2: COMPUTE FARE RANGES PER CLASS
# Ignore zeros and missing fare values
# ─────────────────────────────────────────────────────
def get_fare_ranges(df):
    """
    Calculate min/max fare per class, ignoring zeros and missing values.
    Returns: {class_number: (min_fare, max_fare)}
    """
    df_valid = df[df["fare"] > 0].copy()
    fare_ranges = {}
    for pclass in sorted(df_valid["pclass"].unique()):
        class_fares = df_valid[df_valid["pclass"] == pclass]["fare"]
        fare_ranges[pclass] = (class_fares.min(), class_fares.max())
    return fare_ranges


# ─────────────────────────────────────────────────────
# STEP 3: COMPUTE GLOBAL FARE LIMITS
# ─────────────────────────────────────────────────────
def get_global_fare_limits(df):
    """Return the global (min, max) fare, ignoring zeros and NaN."""
    df_valid = df[df["fare"] > 0].copy()
    return df_valid["fare"].min(), df_valid["fare"].max()


# ─────────────────────────────────────────────────────
# STEP 4: INPUT VALIDATION FUNCTIONS
# Each function loops until a valid value is provided
# ─────────────────────────────────────────────────────
def get_valid_name():
    """Strip leading/trailing spaces. Reject empty strings."""
    while True:
        name = input("Enter passenger name: ").strip()
        if name:
            return name
        print("  ✗  Name cannot be empty. Please try again.")


def get_valid_age():
    """Accept a float age between 0 and 130."""
    while True:
        raw = input("Enter passenger age: ")
        try:
            age = float(raw)
            if 0 <= age <= 130:
                return age
            else:
                print("  ✗  Your age is wrong. Age must be between 0 and 130. Please try again.")
        except ValueError:
            print("  ✗  Your age is wrong. Please enter a valid numeric age.")


def get_valid_sex():
    """Accept only 'male' or 'female' (case-insensitive)."""
    while True:
        raw = input("Enter passenger sex (male/female): ").strip().lower()
        if raw in ("male", "female"):
            return raw
        print("  ✗  The sex value is illegal. Please enter 'male' or 'female'.")


def get_valid_fare(global_min, global_max):
    """Accept a float fare within the global dataset min-max range."""
    while True:
        raw = input(f"Enter fare paid (${global_min:.2f} – ${global_max:.2f}): ")
        try:
            fare = float(raw)
            if global_min <= fare <= global_max:
                return fare
            else:
                print(
                    f"  ✗  Your fare payment is illegal. "
                    f"Fare must be between ${global_min:.2f} and ${global_max:.2f}. "
                    f"Please try again."
                )
        except ValueError:
            print("  ✗  Your fare payment is illegal. Please enter a valid numeric fare.")


# ─────────────────────────────────────────────────────
# STEP 5: CLASSIFY PASSENGER BY FARE
# Preference always goes UP (class 1 > class 2 > class 3)
# ─────────────────────────────────────────────────────
def classify_fare_to_class(fare, fare_ranges):
    """
    Assign the best possible class based on fare.
    Iterates classes 1 → 2 → 3 and returns the FIRST match.
    If fare overlaps multiple ranges, passenger is promoted UP.
    """
    for pclass in sorted(fare_ranges.keys()):  # 1, 2, 3
        low, high = fare_ranges[pclass]
        if low <= fare <= high:
            return pclass
    # Fallback: assign to the lowest class if no match found
    return sorted(fare_ranges.keys())[-1]


# ─────────────────────────────────────────────────────
# STEP 6: GENERATE UNIQUE 6-DIGIT TICKET NUMBER
# ─────────────────────────────────────────────────────
def generate_unique_ticket(existing_tickets):
    """
    Randomise a 6-digit ticket number (100000–999999).
    Re-draws if the number already exists in the dataset.
    """
    while True:
        ticket = random.randint(100000, 999999)
        if str(ticket) not in existing_tickets:
            return ticket


# ─────────────────────────────────────────────────────
# STEP 7: CALCULATE SURVIVAL / DEATH PROBABILITY
# GroupBy: pclass + sex + age_group (under18 / over18)
# ─────────────────────────────────────────────────────
def calculate_survival(df, pclass, sex, age):
    """
    Returns (survival_pct, death_pct) based on historical Titanic data.
    GroupBy: pclass + sex + age_group (under18 / over18).
    Fallback 1: pclass + sex only.
    Fallback 2: pclass only.
    """
    df_valid = df[df["fare"] > 0].copy()
    df_valid["age_group"] = df_valid["age"].apply(
        lambda x: "under18" if pd.notna(x) and x < 18 else ("over18" if pd.notna(x) else None)
    )
    df_valid = df_valid.dropna(subset=["age_group"])

    age_group = "under18" if age < 18 else "over18"

    # Primary lookup: class + sex + age_group
    subset = df_valid[
        (df_valid["pclass"]    == pclass) &
        (df_valid["sex"]       == sex) &
        (df_valid["age_group"] == age_group)
    ]
    # Fallback 1: class + sex only
    if len(subset) == 0:
        subset = df_valid[
            (df_valid["pclass"] == pclass) &
            (df_valid["sex"]    == sex)
        ]
    # Fallback 2: class only
    if len(subset) == 0:
        subset = df_valid[df_valid["pclass"] == pclass]

    survival_rate = subset["survived"].mean()
    death_rate    = 1 - survival_rate
    return round(survival_rate * 100, 1), round(death_rate * 100, 1)


# ─────────────────────────────────────────────────────
# STEP 8: SAVE TICKET TO TEXT FILE
# ─────────────────────────────────────────────────────
def save_ticket(ticket, fare, age, pclass, sex, name, filename="passenger_ticket.txt"):
    """Write the formatted passenger ticket to a .txt file."""
    lines = [
        f"ticket: {str(ticket):<10} | fare: {fare}",
        f"age: {str(age):<13} | class: {pclass}",
        f"sex: {sex:<12} | name: {name}",
    ]
    ticket_text = "\n".join(lines)
    with open(filename, "w") as f:
        f.write(ticket_text)
    return ticket_text


# ─────────────────────────────────────────────────────
# STEP 9: MAIN — RUN THE BOOKING SYSTEM
# ─────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("       🚢  TITANIC TICKET BOOKING SYSTEM  🚢")
    print("=" * 55)

    # ── Load data ──
    df               = load_data("titanic.csv")
    fare_ranges      = get_fare_ranges(df)
    global_min, global_max = get_global_fare_limits(df)
    existing_tickets = set(df["ticket"].dropna().astype(str).tolist())

    print("\nFare ranges per class (zeros/missing values ignored):")
    for cls, (lo, hi) in fare_ranges.items():
        print(f"  Class {cls}: ${lo:.2f} – ${hi:.2f}")
    print()

    # ── Collect & validate inputs ──
    name = get_valid_name()
    age  = get_valid_age()
    sex  = get_valid_sex()
    fare = get_valid_fare(global_min, global_max)

    # ── Classify & generate ticket ──
    pclass = classify_fare_to_class(fare, fare_ranges)
    ticket = generate_unique_ticket(existing_tickets)

    # ── Save ticket to file ──
    ticket_text = save_ticket(ticket, fare, age, pclass, sex, name)

    print("\n" + "─" * 55)
    print("           YOUR PASSENGER TICKET")
    print("─" * 55)
    print(ticket_text)
    print("─" * 55)
    print("  ✓  Ticket saved to 'passenger_ticket.txt'")

    # ── Survival / death message ──
    survival_pct, death_pct = calculate_survival(df, pclass, sex, age)
    first_name = name.split()[0]
    print(f"\nDear {first_name}, your chances to die on our trip are {death_pct}%.")
    print("Enjoy your trip 😊")
    print("=" * 55)


if __name__ == "__main__":
    main()