# Homework #2

Source file: `Python-intro-hw.docx` [cite:601]

## Question 1

Create a list with your identification information. [cite:601]

For example, the list length will be 4. If the value at index `0` is accessed, `list[0]` will return `"Alex"`. Run a `for` loop over the list and print its content. 

## Question 2

Create a dictionary that will include your identification information. Use relevant keys for each field. Use the tuple key for relevant declarations. 

Example: [cite:601]

```python
{('name', 'Last_name'): 'Alex Kuznetsov', 'age': 87, 'phone number': 0527389001}
```

## Question 3

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

At the end of the program, print the new list. [cite:601]

## Question 4

Create a Python program that will count the number of appearances of odd and even values in a list. In case that the program encounters a string, use `break` statement and return a print that says, `"It's a string!!!"`, and nullify the values of odd and even numbers counters. [cite:601]

Example 1: [cite:601]

```python
list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Expected output: [cite:601]

```text
Number of even numbers : 5
Number of odd numbers : 4
```

Example 2: [cite:601]

```python
list = [1, 2, 3, 4, "Oops", 6, 7, 8, 9]
```

Expected output: [cite:601]

```text
It's a string!
```

## Question 5

Write a Python script to generate and print a dictionary that contains a number between `1` and `n` in the form `(x, x+3)`. [cite:601]

Sample dictionary with `n = 5`: [cite:601]

Expected output: [cite:601]

```python
{1: 4, 2: 5, 3: 6, 4: 7, 5: 8}
```

## Question 6

Write a Python script to concatenate the following dictionaries to create a new one. [cite:601]

Sample dictionaries: [cite:601]

```python
dic1 = {1: 10, 2: 20}
dic2 = {3: 30, 4: 40}
dic3 = {5: 50, 6: 60}
```

Expected result: [cite:601]

```python
{1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60}
```

## Question 7

Build a function that will count appearances of each character in the string and will return a dictionary with string characters as keys and the frequency of each character as key value. [cite:601]

Example: [cite:601]

```python
Input string: ' HANNA'
Expected output: {'H': 1, 'A': 2, 'N': 2}
```

## Question 8

Write a Python program to combine two dictionaries, adding values for common keys. [cite:601]

```python
d1 = {'a': 100, 'b': 200, 'c': 300}
d2 = {'a': 300, 'b': 200, 'd': 400}
```

Sample output: [cite:601]

```python
{'a': 400, 'b': 400, 'd': 400, 'c': 300}
```

## Challenges

## Question 9

Build a Python function that takes a list and returns a new list with unique elements of the first list. [cite:601]

Example: [cite:601]

```python
Input list: [1, 2, 3, 3, 3, 3, 4, 5]
Output list: [1, 2, 3, 4, 5]
```

## Question 10

Write a Python program to construct the following pattern, using a nested loop. [cite:601]

```text
1
12
123
1234
12345
123456
1234567
12345678
```

## Question 11

Write a Python program to print the following pattern. [cite:601]

```text
****
*
*
***
*
*
****
```
