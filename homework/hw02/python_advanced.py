## Re'em Mor
## ID: 311117774


# QUESTION 1

class Vehicle:
    def __init__(self, name, max_speed, mileage):
        self.name = name
        self.max_speed = max_speed
        self.mileage = mileage


vehicle1 = Vehicle("Toyota Corolla", 180, 120000)
print(vehicle1.name, vehicle1.max_speed, vehicle1.mileage)


# QUESTION 2

class Bus(Vehicle):
    pass


bus1 = Bus("Mercedes Bus", 140, 300000)
print(bus1.name, bus1.max_speed, bus1.mileage)


# QUESTION 3

class MyString:
    def __init__(self):
        self.text = ""

    # Read a string from the user.
    def get_String(self):
        self.text = input("Enter a string: ")

    def print_String(self):
        print(self.text.upper())


string_obj = MyString()
string_obj.get_String()
string_obj.print_String()


# QUESTION 4

# Write identification information into a text file.
with open("my_id.txt", "w") as file:
    file.write("name: Reem\n")
    file.write("last name: Mor\n")
    file.write("age: 32\n")
    file.write("phone number: 0526775754\n")

# Print the file content to check that it was written correctly.
with open("my_id.txt", "r") as file:
    print(file.read())

# QUESTION 5

def count_word_frequency(file_path):
    word_count = {}

    with open(file_path, "r") as file:
        words = file.read().split()

    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    return word_count


print(count_word_frequency("my_id.txt"))


# QUESTION 6

def longest_label_in_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    longest_label = ""

    for line in lines:
        label = line.split(":")[0].strip()
        if len(label) > len(longest_label):
            longest_label = label

    return longest_label


print(longest_label_in_file("my_id.txt"))

# QUESTION 7

def sum_list(numbers):
    total = 0

    for num in numbers:
        total += num

    return total


print(sum_list([1, 2, 3, 4, 5]))


# QUESTION 8

def multiply_list(numbers):
    result = 1

    for num in numbers:
        result *= num

    return result


print(multiply_list([1, 2, 3, 4, 5]))


# QUESTION 9

def min_list(numbers):
    min_value = numbers[0]

    for num in numbers:
        if num < min_value:
            min_value = num

    return min_value


print(min_list([8, 3, 12, 1, 6]))


# QUESTION 10

def count_upper_lower(text):
    upper_count = 0
    lower_count = 0

    for char in text:
        if char.isupper():
            upper_count += 1
        elif char.islower():
            lower_count += 1

    print(f"Upper case letters: {upper_count}")
    print(f"Lower case letters: {lower_count}")


count_upper_lower("Hello World")


# QUESTION 11

import numpy as np

numbers = np.arange(10)
print(numbers)


# QUESTION 12

arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Extract odd numbers without using loops.
odd_numbers = arr[arr % 2 != 0]

print(odd_numbers)


# QUESTION 13

import numpy as np

eye_array = np.eye(5)

# Replace all values greater than 0 with -1, without loops.
eye_array[eye_array > 0] = -1

print(eye_array)


# QUESTION 14

# Recursive function to calculate a to the power of b.
def power(a, b):
    if b == 0:
        return 1
    return a * power(a, b - 1)


print(power(3, 2))

# QUESTION 15

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def is_empty(self):
        return len(self.items) == 0


# Check if the brackets are closed in the correct order.
def is_valid_parentheses(text):
    stack = Stack()
    pairs = {
        ")": "(",
        "}": "{",
        "]": "["
    }
    valid_chars = set("(){}[]")

    for char in text:
        if char not in valid_chars:
            return False

        if char in "({[":
            stack.push(char)
        else:
            if stack.is_empty() or stack.pop() != pairs[char]:
                return False

    return stack.is_empty()


print(is_valid_parentheses("()"))
print(is_valid_parentheses("()[]{}"))
print(is_valid_parentheses("[)"))
print(is_valid_parentheses("({[)]"))
print(is_valid_parentheses("{{{"))
print(is_valid_parentheses(""))
print(is_valid_parentheses("({[]})"))
print(is_valid_parentheses("abc"))