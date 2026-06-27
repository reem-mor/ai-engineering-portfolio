# Lecture 02 — Python Introduction

**Slides:** [`resources/lecture02.pdf`](../../resources/MANIFEST.md)

---

## Topics Covered

- Lists, tuples, sets, and dictionaries
- List comprehensions and generator expressions
- Control flow: `if/elif/else`, `for`, `while`, `break`, `continue`
- Functions: `def`, `return`, default arguments, `*args`, `**kwargs`
- String methods: `split()`, `join()`, `strip()`, `replace()`, `find()`
- File I/O: `open()`, `read()`, `write()`, context manager `with`
- Exception handling: `try/except/finally`
- Modules and imports

---

## Key Concepts You Must Know

### Collections

| Type | Ordered | Mutable | Duplicates | Syntax |
|------|---------|---------|------------|--------|
| `list` | Yes | Yes | Yes | `[1, 2, 3]` |
| `tuple` | Yes | No | Yes | `(1, 2, 3)` |
| `set` | No | Yes | No | `{1, 2, 3}` |
| `dict` | Yes (3.7+) | Yes | Keys: No | `{"a": 1}` |

- Use a **list** when order and mutability both matter.
- Use a **tuple** for fixed-size records (coordinates, RGB, DB rows).
- Use a **set** for fast membership testing and deduplication.
- Use a **dict** to map keys to values (O(1) average lookup).

### List Comprehensions
```python
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
matrix  = [[r * c for c in range(3)] for r in range(3)]
```
Comprehensions are faster than equivalent `for` loops because they avoid repeated attribute lookups.

### Functions
- Arguments are passed **by assignment** — mutable defaults are shared across calls:
  ```python
  def bad(items=[]):   # DON'T DO THIS
      items.append(1)
      return items

  def good(items=None):  # correct pattern
      if items is None:
          items = []
      items.append(1)
      return items
  ```
- `*args` collects extra positional arguments as a tuple; `**kwargs` collects keyword arguments as a dict.

### File I/O
```python
# Always use a context manager — it closes the file even on exceptions
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()       # entire file as string
    # OR
    lines = f.readlines()    # list of lines including \n
    # OR
    for line in f:           # memory-efficient iteration
        process(line.strip())
```

### Exception Handling
```python
try:
    result = int(user_input)
except ValueError as e:
    print(f"Not a number: {e}")
except (TypeError, OverflowError):
    print("Something else went wrong")
finally:
    print("This always runs")
```

---

## Exercises

### Exercise 1 — List Manipulation
```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
# 1. Remove duplicates while preserving order
# 2. Return only numbers greater than 4
# 3. Return the square of each unique number in one line (comprehension)
```

### Exercise 2 — Dictionary Operations
```python
inventory = {"apple": 5, "banana": 2, "orange": 8, "grape": 0}
# 1. Find the item with the highest count
# 2. Remove items with count == 0
# 3. Return a new dict with counts doubled
```

### Exercise 3 — Word Statistics from a File
Write a function `word_stats(filepath)` that reads a text file and returns a dict:
```python
{
    "lines":  int,    # total number of lines
    "words":  int,    # total word count
    "unique": int,    # number of unique lowercase words
    "top3":   list,   # three most common words [(word, count), ...]
}
```

### Exercise 4 — Functions with `*args`
```python
def running_total(*numbers):
    """Return a list of cumulative sums."""
    # running_total(1, 2, 3, 4) → [1, 3, 6, 10]
```

### Exercise 5 — Exception-Safe Integer Converter
```python
def safe_parse_ints(values: list[str]) -> list[int]:
    """
    Convert a list of strings to integers.
    Skip (do not crash on) strings that are not valid integers.
    safe_parse_ints(["1", "two", "3", "four", "5"]) → [1, 3, 5]
    """
```

---

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| Modifying a list while iterating it | Iterate over a copy: `for item in lst[:]` |
| `dict.keys()` returns a view, not a list | Wrap in `list()` if you need indexing |
| `"hello" in "hello world"` is substring check | Use `word in text.split()` for whole-word check |
| Forgetting `encoding="utf-8"` in `open()` | Always specify encoding — default varies by OS |
