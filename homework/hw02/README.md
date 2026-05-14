# Homework 2

## Part A — Python Intro (Lists & Dictionaries)

### Question 1

Create a list with your identification information.

For example, the list length will be 4. If the value at index `0` is accessed, `list[0]` will return `"Alex"`. Run a `for` loop over the list and print its content.

### Question 2

Create a dictionary that will include your identification information. Use relevant keys for each field. Use the tuple key for relevant declarations.

Example:

```python
{('name', 'Last_name'): 'Alex Kuznetsov', 'age': 87, 'phone number': 0527389001}
```

### Question 3

Create a program that receives two lists of the same length with integers as values. If the lists are not of the same length, the program must return the relevant error. The program will create a new list that will contain the largest value between the two lists at a specific index.

Example input:

```python
lst1 = [1, 2, 3, 4, 5]
lst2 = [5, 4, 3, 2, 1]
```

Expected output:

```python
[5, 4, 3, 4, 5]
```

### Question 4

Create a Python program that will count the number of appearances of odd and even values in a list. In case that the program encounters a string, use `break` statement and return a print that says `"It's a string!!!"`, and nullify the values of odd and even numbers counters.

### Question 5

Write a Python script to generate and print a dictionary that contains a number between `1` and `n` in the form `(x, x+3)`.

Sample dictionary with `n = 5`:

```python
{1: 4, 2: 5, 3: 6, 4: 7, 5: 8}
```

### Question 6

Write a Python script to concatenate the following dictionaries to create a new one.

```python
dic1 = {1: 10, 2: 20}
dic2 = {3: 30, 4: 40}
dic3 = {5: 50, 6: 60}
```

Expected result:

```python
{1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60}
```

### Question 7

Build a function that will count appearances of each character in the string and will return a dictionary with string characters as keys and the frequency of each character as key value.

Example:

```python
Input string: ' HANNA'
Expected output: {'H': 1, 'A': 2, 'N': 2}
```

### Question 8

Write a Python program to combine two dictionaries, adding values for common keys.

```python
d1 = {'a': 100, 'b': 200, 'c': 300}
d2 = {'a': 300, 'b': 200, 'd': 400}
```

Expected output:

```python
{'a': 400, 'b': 400, 'd': 400, 'c': 300}
```

### Challenges

#### Question 9

Build a Python function that takes a list and returns a new list with unique elements of the first list.

#### Question 10

Write a Python program to construct the following pattern using a nested loop:

```
1
12
123
1234
12345
123456
1234567
12345678
```

#### Question 11

Write a Python program to print the following pattern:

```
****
*
*
***
*
*
****
```

---

## Part B — OOP, Files & NumPy

### Question 1 — Vehicle class

Create a new class named `Vehicle`.

Requirements:

- Add `name`, `max_speed`, and `mileage` as parameters inside the `__init__` function.
- Create one `Vehicle` object.

### Question 2 — Bus class

Create a child class named `Bus` that inherits from the `Vehicle` class.

Requirements:

- The `Bus` class should inherit all variables and methods from `Vehicle`.
- Create one `Bus` object.

### Question 3 — String methods class

Write a Python class with two methods:

- `get_String` — accepts a string from the user.
- `print_String` — prints the string in uppercase.

### Question 4 — Text file

Write a text file with your identification information.

Requirements:

- The file name must be `my_id.txt`.

### Question 5 — Word frequency in a file

Write a Python function that counts how many times each word appears in a text file.

Requirements:

- The function should receive the path of the `.txt` file as input.
- The function should return a dictionary where each key is a word and each value is its count.

### Question 6 — Longest word in a file

Write a Python program that finds the longest word in a text file.

### Question 7 — Sum of a list

Build a function that receives a list of integers as input, calculates the sum, and returns it.

### Question 8 — Multiply all values in a list

Build a function that receives a list of integers as input, multiplies all values, and returns the result.

### Question 9 — Minimal value in a list

Build a function that receives a list of integers as input and returns the minimum value.

### Question 10 — Count uppercase and lowercase letters

Build a Python function that accepts a string and counts uppercase and lowercase letters separately.

### Question 11 — NumPy array from 0 to 9

Create a 1D NumPy array with numbers from `0` to `9` without using any loops.

### Question 12 — Extract odd numbers from a NumPy array

Create a 1D NumPy array and extract all odd numbers into a new array without using any loops.

### Challenges

#### Challenge 13 — 5x5 NumPy eye array

Create a `5 x 5` 2D NumPy eye array and replace all values greater than `0` with `-1` without using any loops.

#### Challenge 14 — Recursive power function

Create a recursive function that calculates `a` to the power of `b`.

#### Challenge 15 — Valid parentheses

Write a Python program that checks whether a string of parentheses and brackets is valid using a `Stack` class structure.
