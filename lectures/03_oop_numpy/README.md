# Lecture 03 — Object-Oriented Programming & NumPy

**Slides:** [`resources/lecture03.pdf`](../../resources/MANIFEST.md)

---

## Topics Covered

- Classes: `__init__`, instance methods, class variables, `self`
- Inheritance and method overriding, `super()`
- Special (dunder) methods: `__str__`, `__repr__`, `__len__`, `__eq__`
- NumPy array creation and properties (`ndarray`, `shape`, `dtype`)
- Array indexing, slicing, boolean masking
- Vectorised operations and broadcasting
- `np.argmax`, `np.argsort`, `np.where`, `np.mean`, `np.std`
- Recursion: base case, recursive case, call stack
- Stack data structure and real-world application (bracket matching)

---

## Key Concepts You Must Know

### Classes

```python
class Animal:
    species_count = 0          # class variable — shared by all instances

    def __init__(self, name: str, sound: str):
        self.name = name       # instance variable — unique per object
        self.sound = sound
        Animal.species_count += 1

    def speak(self) -> str:
        return f"{self.name} says {self.sound}"

    def __repr__(self) -> str:
        return f"Animal(name={self.name!r})"


class Dog(Animal):
    def __init__(self, name: str):
        super().__init__(name, "woof")  # delegate to parent __init__

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}!"
```

Key rules:
- Every instance method receives `self` as its first argument.
- `__str__` is for human-readable output (`str(obj)`); `__repr__` is for unambiguous debugging.
- Use `isinstance(obj, ClassName)` to check type without breaking inheritance.

### Inheritance
- A subclass inherits all methods and attributes of the parent.
- Override a method by redefining it in the subclass.
- Call the parent's version with `super().method_name()`.
- Python supports multiple inheritance; Method Resolution Order (MRO) is left-to-right, depth-first.

### NumPy

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
b = np.arange(0, 10, 2)          # [0, 2, 4, 6, 8]
c = np.zeros((3, 4))             # 3×4 matrix of zeros
d = np.random.rand(5)            # 5 uniform random floats in [0, 1)

# Vectorised ops — no Python loop needed
print(a * 2)          # [2, 4, 6, 8, 10]
print(a[a > 3])       # boolean mask → [4, 5]
print(np.mean(a))     # 3.0

# Broadcasting: arrays with compatible shapes operate element-wise
row = np.array([[1, 2, 3]])      # shape (1, 3)
col = np.array([[10], [20]])     # shape (2, 1)
print(row + col)                 # shape (2, 3) — broadcast
```

Broadcasting rules (applied dimension by dimension, right to left):
1. Dimensions are equal → OK.
2. One of them is 1 → stretch that dimension.
3. Otherwise → shape mismatch error.

### Recursion
A recursive function must have:
1. **Base case** — a condition that returns without recursing.
2. **Recursive case** — call itself with a simpler/smaller input.

```python
def factorial(n: int) -> int:
    if n <= 1:          # base case
        return 1
    return n * factorial(n - 1)   # recursive case
```

Python's default recursion limit is 1000 (`sys.setrecursionlimit()`). For deep recursion, prefer iteration.

### Stack
A stack is LIFO (Last-In First-Out). Implemented with a Python list:

```python
stack = []
stack.append("a")   # push
stack.append("b")
top = stack.pop()   # pop → "b"
peek = stack[-1]    # look without removing → "a"
```

---

## Exercises

### Exercise 1 — Vehicle Hierarchy
```python
# Create a Vehicle base class with: make, model, year, fuel_level (0–100)
# Methods: refuel(amount), drive(km) → reduces fuel
# Subclass Bus: adds capacity (seats), is_full() method
# Override __str__ in both classes
```

### Exercise 2 — NumPy Statistics
```python
data = np.array([12, 45, 7, 23, 67, 3, 89, 34, 56, 11])
# 1. Index of the maximum value
# 2. All values above the mean
# 3. Sorted indices (argsort)
# 4. Replace values below 10 with 0 (np.where)
```

### Exercise 3 — Matrix Operations
```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
# 1. Element-wise product
# 2. Matrix multiplication (np.dot or @)
# 3. Transpose of A
# 4. Determinant using np.linalg.det
```

### Exercise 4 — Recursive Fibonacci
```python
def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number (0-indexed).
    fibonacci(0)=0, fibonacci(1)=1, fibonacci(7)=13
    """
```

### Exercise 5 — Bracket Validator
```python
def is_balanced(s: str) -> bool:
    """
    Return True if all brackets are matched and properly nested.
    is_balanced("({[]})") → True
    is_balanced("([)]")   → False
    is_balanced("{[}")     → False
    """
```

---

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| `np.array([1,2,3]) * np.array([1,2])` | Shapes must be broadcast-compatible |
| Mutating a NumPy array while iterating | Use boolean masking instead of explicit loops |
| Forgetting `super().__init__()` in subclass | Parent `__init__` code won't run without it |
| Infinite recursion | Make sure the base case is reachable from all inputs |
| `stack[-1]` on empty list raises `IndexError` | Check `if stack:` before accessing |
