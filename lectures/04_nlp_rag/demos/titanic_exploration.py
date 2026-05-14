"""Demo: quick pandas exploration of the Titanic dataset."""
from pathlib import Path
import pandas as pd

CSV_PATH = Path(__file__).parent.parent.parent.parent / "homework" / "hw03" / "data" / "titanic.csv"

df = pd.read_csv(CSV_PATH)
print(f"Dataset shape: {df.shape}")

women = df[df.sex == "female"]
women_lost = women[women.survived == 0]
print(f"\nWomen who did not survive: {len(women_lost)} / {len(women)} "
      f"({len(women_lost) / len(women) * 100:.1f}%)")

men = df[df.sex == "male"]
print(f"Total men: {len(men)}")

minors = df[df.age < 18]
print(f"Passengers under 18: {len(minors)}")
