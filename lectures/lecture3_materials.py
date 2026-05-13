import pandas as pd
csv_path = ('titanic.csv')

df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()

females = df[df["sex"] == "female"]
males = df[df["sex"] == "male"]
minors = df[df["age"] < 18]

num_female_passengers = len(females)
num_male_passengers = len(males)
num_minor_passengers = len(minors)

percent_survived_females = females["survived"].mean() * 100
percent_survived_males = males["survived"].mean() * 100
percent_survived_minors = minors["survived"].mean() * 100

print(f"Female passengers: {num_female_passengers}")
print(f"Male passengers: {num_male_passengers}")
print(f"Minor passengers (<18): {num_minor_passengers}")
print(f"Survived females: {percent_survived_females:.2f}%")
print(f"Survived males: {percent_survived_males:.2f}%")
print(f"Survived minors: {percent_survived_minors:.2f}%")

