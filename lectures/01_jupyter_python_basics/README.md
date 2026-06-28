# Lecture 01 — Jupyter & Python Basics

**Slides:** [`resources/lecture01.pdf`](../../resources/MANIFEST.md)

---

## Topics Covered

- Jupyter Notebook interface: code cells, Markdown cells, kernel
- Python primitive types: `int`, `float`, `str`, `bool`
- Variables and assignment
- Arithmetic and comparison operators
- String slicing, concatenation, and f-strings
- Built-in functions: `print()`, `len()`, `type()`, `input()`
- `matplotlib` basics: creating figures, drawing shapes
- Jupyter magic commands: `%matplotlib inline`, `%timeit`

---

## Key Concepts You Must Know

### Jupyter
- A **Notebook** is a `.ipynb` file containing an ordered list of cells.
- **Code cells** execute Python; output appears directly below.
- **Markdown cells** render formatted text (headings, bold, lists, LaTeX math).
- `Shift+Enter` runs the current cell and moves to the next. `Ctrl+Enter` runs in-place.
- The **kernel** is the Python process. Restart it (`Kernel → Restart`) to clear all variables.
- Cell execution order matters — variables are shared across all cells in the same kernel session.

### Python Basics
- Python is **dynamically typed**: the type is attached to the value, not the variable name.
- Integer division uses `//`; modulo uses `%`; exponentiation uses `**`.
- Strings are **immutable sequences**: `s[0]` reads a char; `s[1:4]` slices; you cannot assign `s[0] = 'X'`.
- f-strings (`f"Hello {name}"`) are the preferred way to interpolate values (Python 3.6+).

### matplotlib
- `import matplotlib.pyplot as plt` is the standard import alias.
- `plt.show()` is needed in scripts; in Jupyter use `%matplotlib inline` to auto-display.
- A circle: `plt.Circle((cx, cy), radius)` added to an axis with `ax.add_patch(circle)`.

---

## Exercises

### Exercise 1 — Markdown Cell Formatting
Create a Markdown cell that renders:
- A level-2 heading "My Profile"
- Your name in **bold** and hometown in *italics*
- A numbered list of three programming languages you know

### Exercise 2 — Variable Calculations
```python
# Given the following, compute and print the results:
name = "Ada"
birth_year = 1990
gpa = 3.85

age = ...          # current year minus birth_year
initials = ...     # first letter of name
gpa_str = ...      # gpa formatted to 1 decimal place using an f-string
```

### Exercise 3 — String Slicing
```python
text = "Python Programming"
# Expected outputs:
# First word:  "Python"
# Last word:   "Programming"
# Reversed:    "gnimmargorP nohtyP"
# Every 2nd char: "Pto rgamn"
```

### Exercise 4 — Pythagorean Theorem
Write a function `hypotenuse(a, b)` that returns the length of the hypotenuse.
Test it with `a=3, b=4` → expected `5.0`.

### Exercise 5 — Matplotlib Circles
Draw three concentric circles with radii 1, 2, and 3. Set equal aspect ratio so they look round.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
for r in [1, 2, 3]:
    ax.add_patch(plt.Circle((0, 0), r, fill=False))
ax.set_xlim(-4, 4)
ax.set_ylim(-4, 4)
ax.set_aspect("equal")
plt.show()
```

---

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| `1/3` gives `0.33...` but you expected integer | Use `1//3` for integer division |
| Markdown cell not rendering | Make sure cell type is set to *Markdown* not *Code* |
| `NameError` on a variable you defined | You may have skipped a cell — run cells in order |
| `plt.show()` produces blank output in Jupyter | Add `%matplotlib inline` in the first cell |
