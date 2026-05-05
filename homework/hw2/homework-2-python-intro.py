## Re'em Mor
## 311117774


# QUESTION1

my_info = ["Reem", "Mor", 25, "0521234567"]

for item in my_info:
    print(item)

# QUESTION2

my_info_dict = {
    ("name", "last_name"): "Reem Mor",
    "age": 32,
    "phone number": "0526775754",
}

print(my_info_dict)
# Question 3


def max_list(lst1, lst2):
    if len(lst1) != len(lst2):
        raise ValueError("Lists must be of the same length")

    return [max(a, b) for a, b in zip(lst1, lst2)]


# Question 4


def count_even_odd(values):
    even_count = 0
    odd_count = 0

    for item in values:
        if isinstance(item, str):
            print("It's a string!")
            return  # immediately stop (cleaner than break + flags)

        if item % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    print(f"Number of even numbers: {even_count}")
    print(f"Number of odd numbers: {odd_count}")


# Tests
count_even_odd([1, 2, 3, 4, 5, 6, 7, 8, 9])
count_even_odd([1, 2, 3, 4, "Oops", 6, 7, 8, 9])

# Question 5


def generate_formula_dict(n):
    result_dict = {}
    for x in range(1, n + 1):
        result_dict[x] = x + 3
    return result_dict


n = 5
print(generate_formula_dict(n))

# Question 6

dic1 = {1: 10, 2: 20}
dic2 = {3: 30, 4: 40}
dic3 = {5: 50, 6: 60}

# Combining using the built-in update method
result_dict = {}
result_dict.update(dic1)
result_dict.update(dic2)
result_dict.update(dic3)

print(result_dict)


# Question 7

# QUESTION6

def count_characters(text):
    char_count = {}

    for char in text:
        if char != " ":
            char_count[char] = char_count.get(char, 0) + 1

    return char_count


result = count_characters("HANNA")
print(result)

# Question 8

def merge_and_sum(d1: dict, d2: dict) -> dict:
    result = d1.copy()  # avoid mutating original

    for key, value in d2.items():
        result[key] = result.get(key, 0) + value

    return result


# Example
d1 = {'a': 100, 'b': 200, 'c': 300}
d2 = {'a': 300, 'b': 200, 'd': 400}

output = merge_and_sum(d1, d2)
print(output)

# Question 9


def unique_list(numbers):
    new_list = []

    for item in numbers:
        if item not in new_list:
            new_list.append(item)

    return new_list


print(unique_list([1, 2, 3, 3, 3, 3, 4, 5]))

#Question 10

def print_pattern(n: int = 8):
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            print(j, end="")
        print()  # new line


# Example
print_pattern()

#Question 11

def print_custom_star_pattern():
    # Defining the structure using conditional logic
    for row in range(7):
        if row == 0 or row == 6:
            print("****")
        elif row == 1 or row == 2:
            print("*")
        elif row == 3:
            print("  ***")
        else:
            print("     *")

print_custom_star_pattern()