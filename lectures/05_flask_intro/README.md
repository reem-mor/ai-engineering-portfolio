# Lecture 05 — Flask Introduction

**Slides:** [`resources/lecture04_flask_intro.pdf`](../../resources/lecture04_flask_intro.pdf)

---

## Topics Covered

- WSGI and the Flask request-response cycle
- Application factory: `Flask(__name__)`
- Route decorators: `@app.route(path, methods=[...])`
- URL variables and type converters: `<int:id>`, `<string:name>`
- Returning strings, HTML, and JSON from views
- Jinja2 template engine: `render_template()`, `extends`, `block`, `url_for()`
- Static files: `url_for('static', filename='css/main.css')`
- Debug mode and the auto-reloader
- Running the app: `flask run` vs `python app.py`

---

## Key Concepts You Must Know

### The Flask Request Cycle

```
Browser                Flask App
  │  HTTP GET /        │
  │──────────────────▶│
  │                    │  1. Match URL → route function
  │                    │  2. Execute route function
  │                    │  3. Return Response
  │◀──────────────────│
  │  HTML / JSON       │
```

### Minimal App

```python
from flask import Flask

app = Flask(__name__)   # __name__ tells Flask where to look for templates/static

@app.route("/")
def home():
    return "Hello World!"

@app.route("/user/<name>")          # URL variable
def greet(name: str):
    return f"<h1>Hello, {name}!</h1>"

if __name__ == "__main__":
    app.run(debug=True)             # debug=True: auto-reload + error pages
```

### Templates (Jinja2)

Jinja2 extends HTML with template logic. Flask looks for templates in `templates/`.

**base.html** (parent layout):
```html
<!doctype html>
<html>
<head>
  <title>{% block title %}My App{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
</head>
<body>
  <nav>
    <a href="{{ url_for('home') }}">Home</a>
  </nav>
  <main>{% block content %}{% endblock %}</main>
</body>
</html>
```

**page.html** (child):
```html
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block content %}
  <h1>{{ heading }}</h1>
  {% for item in items %}
    <p>{{ item }}</p>
  {% endfor %}
{% endblock %}
```

**Route passing context to template:**
```python
@app.route("/items")
def items():
    return render_template("page.html", heading="My Items", items=["A", "B", "C"])
```

### Jinja2 Syntax Quick Reference

| Syntax | Purpose |
|--------|---------|
| `{{ variable }}` | Output a variable |
| `{% for x in list %}...{% endfor %}` | Loop |
| `{% if condition %}...{% endif %}` | Conditional |
| `{% extends "base.html" %}` | Inherit from a parent template |
| `{% block name %}...{% endblock %}` | Define/override a content region |
| `{{ url_for('view_name') }}` | Generate a URL for a named route |

### Static Files
Flask serves anything inside `static/` at `/static/<path>`.

```
05_flask_intro/
├── static/
│   └── css/
│       ├── main.css    ← shared styles
│       └── about.css   ← page-specific styles
└── templates/
    ├── base.html
    ├── index.html
    └── about.html
```

Reference in a template: `{{ url_for('static', filename='css/main.css') }}`

### HTTP Methods
```python
from flask import request

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # validate...
    return render_template("login.html")
```

---

## Running the Demo App

```bash
cd lectures/05_flask_intro
python app.py
# Open http://127.0.0.1:5000/
```

---

## Exercises

### Exercise 1 — New Route
Add a `/contact` route that renders a new `contact.html` template extending `base.html`.
The page should display a heading and a dummy contact form (no backend needed).

### Exercise 2 — URL Variable
Add a `/greet/<name>` route. It should render a page that says "Hello, {name}! Welcome."
If `name` contains only digits, return a 400 Bad Request with a JSON error message.

### Exercise 3 — Context to Template
Add a `/fruits` route that passes a list of fruits to a template.
The template should render them as an unordered list (`<ul>`).

### Exercise 4 — JSON API Endpoint
Add a `/api/info` route that returns JSON:
```json
{"app": "Flask Demo", "version": "1.0", "routes": ["/", "/about", "/api/info"]}
```
Use `jsonify()`. Test it with your browser or `curl http://127.0.0.1:5000/api/info`.

---

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| `TemplateNotFound` | Check the file is in `templates/` and the name matches exactly |
| `url_for()` raises `BuildError` | The argument must be the **function name**, not the URL path |
| Static file returns 404 | File must be inside `static/`; use `url_for('static', ...)` |
| Reloader not triggering | Make sure `debug=True` is set |
| Two routes with the same path | Flask raises `AssertionError` at startup |
