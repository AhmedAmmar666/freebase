# Freebase — Django integration

A drop-in directory page for free dev tools. Dark editorial design, search + category filter, all rendered server-side by Django and progressively enhanced with a tiny vanilla JS file.

## File layout

Copy these files into your Django project, keeping the structure:

```
your_project/
├── your_app/
│   └── views.py            ← from app/views.py (merge with your existing views)
├── templates/
│   └── index.html          ← from templates/index.html
└── static/
    ├── css/style.css       ← from static/css/style.css
    └── js/main.js          ← from static/js/main.js
```

## Wire it up

**1. Settings** (`settings.py`) — make sure you have:

```python
INSTALLED_APPS = [..., "your_app"]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    ...
}]
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

**2. URLs** (`your_project/urls.py`):

```python
from django.urls import path
from your_app import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

**3. Run:**

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## How it works

- **`views.py`** holds the `TOOLS` list and `CATEGORIES`. It computes `host` for each tool from the URL and passes everything to the template context.
- **`index.html`** uses `{% for tool in tools %}` to render each card and `{% for cat in categories %}` for the filter chips. All styling hooks (accent colors, featured layout) come from CSS classes generated from tool fields.
- **`main.js`** filters cards client-side by toggling a `.hidden` class. No framework, no build step.
- **`style.css`** owns all the visual design — typography (Space Grotesk + Inter from Google Fonts), warm-dark palette, animated cards, sticky filters, grain overlay.

## Adding tools

Edit the `TOOLS` list in `views.py`. Required fields: `name`, `tagline`, `description`, `url`, `category`, `accent` (one of `lime`, `coral`, `violet`, `sky`), `glyph`. Optional: `featured: True` makes the card span 2 columns on desktop.

## Want a database instead?

Convert `TOOLS` into a `Tool` model and replace the list in `index()` with `Tool.objects.all()`. The template and JS need no changes.
