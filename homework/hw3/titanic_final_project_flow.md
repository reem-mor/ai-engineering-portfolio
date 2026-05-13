# Titanic Ride Ticket Classifier — Final Project Flow

## Project goal
Build a Python system that allows a new passenger to join the Titanic trip, validates the passenger input, classifies the passenger into the best class based on fare ranges, generates a unique ticket number, saves the ticket to a text file, and estimates the passenger's survival or death probability from the historical Titanic dataset.

## Authoritative requirements
This final version follows the teacher explanation:
- Input is received interactively with `input()` for `name`, `age`, `fare`, and `sex`.
- `sex` must be only `male` or `female`.
- `age` must be between 0 and 130.
- `name` must be a valid non-empty string after cleaning.
- `fare` must be a valid float number.
- When analyzing fare ranges by class, zero fares and missing fares are ignored.
- If fare ranges overlap, the passenger is promoted to the best possible class.
- Survival is estimated using `pclass + sex + age_group`, where age group is `under18` or `over18`.

## Inputs
The program receives:
- `name` as a string.
- `age` as a string that must be converted to `float`.
- `fare` as a string that must be converted to `float`.
- `sex` as a string.

## Data preparation flow
1. Load the Titanic CSV with pandas.
2. Keep the columns needed for the task: `pclass`, `survived`, `sex`, `age`, `ticket`, `fare`.
3. Convert `fare` and `age` to numeric values with `errors="coerce"`.
4. For fare-range analysis, remove rows where `fare` is missing or equal to 0.
5. Calculate min and max fare for each `pclass`.
6. Load existing ticket numbers and store them in a set for fast lookup.

## Input validation flow
### Name
- Read the input as text.
- Use `.strip()` to remove leading and trailing spaces.
- If the result is empty, ask again.

### Age
- Read the input as text.
- Convert to `float` inside `try/except`.
- If conversion fails, ask again.
- If age is outside 0 to 130, ask again.

### Sex
- Read the input as text.
- Clean with `.strip().lower()`.
- Accept only `male` or `female`.
- Otherwise print an error and ask again.

### Fare
- Read the input as text.
- Convert to `float` inside `try/except`.
- If conversion fails, ask again.
- In this teacher version, fare must be a valid float; class assignment is based on cleaned historical fare ranges.

## Class assignment logic
1. Build fare ranges for each class after ignoring zero and missing fares.
2. Check which class ranges contain the passenger fare.
3. If the fare fits more than one class, return the best class, meaning the smallest class number.
4. If no class matches exactly, assign the nearest sensible class by business rule, usually based on closest valid range or by informing the user that the fare does not map clearly.

### Example
- Class 1: 100 to 300
- Class 2: 50 to 200
- Class 3: 20 to 150
- Fare = 140

This fare fits all three classes, so the passenger is promoted to Class 1.

## Ticket generation flow
1. Generate a random 6-digit number.
2. Check whether it already exists in the Titanic ticket values or in newly generated numbers.
3. If it exists, generate again.
4. Continue until a unique ticket number is found.

## Ticket file output
The ticket must be written to a text file in this format:

```text
ticket: 111111 | fare: 175

age: 76        | class: 1

sex: male      | name: Alex Kuznetsov
```

## Survival calculation flow
1. Create an `age_group` column:
   - `under18` if age < 18
   - `over18` if age >= 18
2. Group the dataset by `pclass`, `sex`, and `age_group`.
3. Compute the mean of `survived` for each group.
4. For the new passenger, find the matching subgroup.
5. Survival probability = `mean(survived) * 100`.
6. Death probability = `100 - survival_probability`.
7. Round the displayed percentage to one decimal place.

### Fallback best practice
If the exact subgroup does not exist, use fallback levels in this order:
1. `pclass + sex + age_group`
2. `pclass + sex`
3. `pclass`
4. overall dataset survival

## Final user message
Example output:

```text
Dear Alex, your chances to die on our trip are 73.7%.
Enjoy your trip ☺
```

## Edge cases to check
- Name contains only spaces.
- Age is not numeric.
- Age is below 0 or above 130.
- Sex is not `male` or `female`.
- Fare is not numeric.
- Fare falls into overlapping class ranges.
- Generated ticket already exists.
- Exact survival subgroup is missing.
- Age is missing in dataset rows used for groupby.
- Ticket column contains non-6-digit original values, so uniqueness should be checked as strings.

## Recommended function structure
- `load_data(filepath)`
- `get_fare_ranges(df)`
- `get_existing_tickets(df)`
- `get_valid_name()`
- `get_valid_age()`
- `get_valid_sex()`
- `get_valid_fare()`
- `classify_fare_to_class(fare, fare_ranges)`
- `calculate_survival(df, pclass, sex, age)`
- `generate_unique_ticket(existing_tickets)`
- `save_ticket(ticket_no, fare, age, pclass, sex, name, output_path)`
- `main()`

## Best-practice implementation notes
- Keep each function responsible for one job.
- Use pandas for data loading and grouping.
- Use sets for fast ticket uniqueness checks.
- Use `.copy()` when filtering DataFrames before modifying columns.
- Add clear docstrings and readable variable names.
- Keep the notebook version educational and the `.py` version production-style but still simple.
