"""Render the app to a static site for GitHub Pages.

Run from the directory containing manage.py:

    python build_demo.py

Output lands in ../docs, which GitHub Pages can serve directly
(Settings -> Pages -> Source: main branch, /docs folder).

The result is a pre-rendered snapshot: navigation, styling, charts and the
client-side controls all work, but anything needing a server (upload, training,
sign-in) is inert and the page says so.
"""
import io
import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Graphs.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.test import Client  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR.parent / "docs"
STATIC_SRC = BASE_DIR / "member1" / "static"
REPO_URL = "https://github.com/SankalpVaish/Django"

DEMO_USER = "demo_builder"

# A dataset with numeric and categorical columns so the profile page shows
# histograms, pie charts, boxplots and a correlation matrix.
SAMPLE_ROWS = [
    "Id,Age,Income,LoanAmount,CreditScore,Employment,Education,Approved",
]
_EMPLOYMENT = ["Salaried", "Self-employed", "Contract"]
_EDUCATION = ["Graduate", "Not Graduate"]
for _i in range(48):
    _age = 24 + (_i * 7) % 38
    _income = 28000 + (_i * 3100) % 72000
    _loan = 60000 + (_i * 5700) % 190000
    _score = 560 + (_i * 13) % 300
    _approved = 1 if (_score > 660 and _loan < _income * 3.2) else 0
    SAMPLE_ROWS.append(
        "%d,%d,%d,%d,%d,%s,%s,%d"
        % (
            _i + 1,
            _age,
            _income,
            _loan,
            _score,
            _EMPLOYMENT[_i % 3],
            _EDUCATION[_i % 2],
            _approved,
        )
    )
SAMPLE_CSV = "\n".join(SAMPLE_ROWS) + "\n"

# Server-side routes mapped onto flat filenames.
ROUTE_MAP = {
    "/": "index.html",
    "/graph/": "graph.html",
    "/graph": "graph.html",
    "/ModelTraining/": "model-training.html",
    "/about/": "about.html",
    "/help/": "contact.html",
    "/preference/": "preferences.html",
    "/signup/": "signup.html",
    "/accounts/login/": "login.html",
    "/accounts/logout/": "login.html",
    "/accounts/password_reset/": "password-reset.html",
    "/accounts/password_reset/done/": "password-reset-sent.html",
}

BANNER = """
<style>
.demo-note{{display:flex;gap:.75rem;align-items:flex-start;padding:.85rem 1.1rem;
margin-bottom:1.75rem;border:1px solid #fde68a;border-radius:12px;background:#fffbeb;
color:#92400e;font-size:.875rem;line-height:1.55}}
.demo-note i{{margin-top:.15rem}}
.demo-note a{{color:#92400e;font-weight:600;text-decoration:underline}}
.demo-toast{{position:fixed;left:50%;bottom:1.5rem;transform:translate(-50%,1rem);
z-index:2000;padding:.7rem 1.1rem;border-radius:10px;background:#0f172a;color:#fff;
font-size:.875rem;box-shadow:0 12px 32px -12px rgba(15,23,42,.5);opacity:0;
transition:opacity .25s ease,transform .25s ease;pointer-events:none}}
.demo-toast.is-on{{opacity:1;transform:translate(-50%,0)}}
</style>
<div class="demo-note">
  <i class="bi bi-info-circle-fill"></i>
  <div><strong>Static demo.</strong> This is a pre-rendered snapshot hosted on GitHub
  Pages, so uploading data, training models and signing in are disabled. Browsing,
  layout and all charts are real output from the app.
  <a href="{repo}">View the source</a> to run it locally with live data.</div>
</div>
""".format(repo=REPO_URL)

INERT_SCRIPT = """
<div class="demo-toast" id="demoToast"></div>
<script>
(function () {
  var toast = document.getElementById('demoToast');
  var timer;

  function say(message) {
    toast.textContent = message;
    toast.classList.add('is-on');
    clearTimeout(timer);
    timer = setTimeout(function () { toast.classList.remove('is-on'); }, 3200);
  }

  document.addEventListener('submit', function (event) {
    event.preventDefault();
    say('This is a static demo \\u2014 run the project locally to submit data.');
  });

  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener('click', function (event) {
      event.preventDefault();
      say('File upload needs the Django server \\u2014 not available in this demo.');
    });
  });
})();
</script>
"""

referenced_static = set()


def _map_url(value):
    """Rewrite one server URL into its static-site equivalent."""
    if not value or value.startswith(("http://", "https://", "#", "mailto:", "data:")):
        return value

    # Static assets keep their path, minus the leading slash and cache-buster.
    if value.startswith("/static/"):
        path = value[len("/static/") :].split("?")[0]
        # calc.py builds image paths with Windows separators, which survive
        # {% static %} as %5C. Normalise both forms for the web.
        path = unquote(path).replace("\\", "/")
        referenced_static.add(path)
        return "static/" + path

    clean = value.split("?")[0]

    if clean in ROUTE_MAP:
        return ROUTE_MAP[clean]
    if clean.startswith("/OutlierAnalysis/"):
        return outlier_page(clean[len("/OutlierAnalysis/") :])
    if clean.startswith("/ModelTraining/"):
        return "model-training.html"

    return value


def column_of(image_path):
    """'images\\boxplot\\Income.jpeg' -> 'Income' (matches views.OutAnalysis)."""
    return unquote(image_path).replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]


def outlier_page(image_path):
    return "outlier-%s.html" % column_of(image_path).lower()


ATTR_RE = re.compile(r'\b(href|action|src|data-url)="([^"]*)"')
MAIN_RE = re.compile(r'(<main class="app-main[^"]*">)')


def rewrite(html):
    html = ATTR_RE.sub(
        lambda m: '%s="%s"' % (m.group(1), _map_url(m.group(2))), html
    )
    html = MAIN_RE.sub(lambda m: m.group(1) + BANNER, html, count=1)
    html = html.replace("</body>", INERT_SCRIPT + "</body>")
    return html


copied_static = set()


def save(name, response, transform=None):
    if response.status_code != 200:
        raise SystemExit("%s returned HTTP %s" % (name, response.status_code))
    html = rewrite(response.content.decode())
    if transform:
        html = transform(html)
    (OUT_DIR / name).write_text(html, encoding="utf-8")
    print("  %-26s %6.1f KB" % (name, len(html) / 1024))
    return response.content.decode()


def copy_static():
    """Copy every static file referenced so far, never overwriting.

    Called before the outlier pages run, because those regenerate the boxplot
    images in place and the profile page should keep the unclipped versions.
    """
    for rel in sorted(referenced_static - copied_static):
        src = STATIC_SRC / Path(rel)
        if not src.exists():
            print("  MISSING  %s" % rel)
            continue
        dest = OUT_DIR / "static" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied_static.add(rel)


def main():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    user, created = User.objects.get_or_create(
        username=DEMO_USER, defaults={"email": "demo@example.com"}
    )

    print("Rendering pages:")

    anon = Client()
    save("login.html", anon.get("/accounts/login/"))
    save("signup.html", anon.get("/signup/"))
    save("password-reset.html", anon.get("/accounts/password_reset/"))
    save("password-reset-sent.html", anon.get("/accounts/password_reset/done/"))

    client = Client()
    client.force_login(user)

    save("about.html", client.get("/about/"))
    save("contact.html", client.get("/help/"))
    save("preferences.html", client.get("/preference/"))

    upload = io.BytesIO(SAMPLE_CSV.encode())
    upload.name = "loan_applications.csv"
    client.post("/", data={"myfile": upload})

    # The plot response carries both the builder and a rendered chart.
    save(
        "index.html",
        client.post(
            "/", data={"graph": "scatter", "opt1": "Income", "opt2": "LoanAmount"}
        ),
    )

    # Profiling one-hot encodes the working frame, which training depends on.
    profile = save(
        "graph.html",
        client.post("/graph/", data={"target": "Approved", "mode": "Classification"}),
    )
    save(
        "model-training.html",
        client.get("/ModelTraining/Logistic Regression/?split=25&scaler=standard"),
    )

    # Freeze the unclipped boxplots before outlier analysis rewrites them.
    copy_static()

    # Kept last: this view reloads the unencoded frame and would break training.
    boxplots = dict.fromkeys(
        re.findall(r'href="/OutlierAnalysis/([^"?]+)"', profile)
    )
    for image_path in boxplots:
        col = column_of(image_path)
        clipped = "static/images/outlier/%s.jpeg" % col
        save(
            outlier_page(image_path),
            client.get("/OutlierAnalysis/" + unquote(image_path)),
            # Point at a copy, so this page shows the post-clipping boxplot
            # while the profile page keeps the original.
            lambda html, col=col, clipped=clipped: html.replace(
                "static/images/boxplot/%s.jpeg" % col, clipped
            ),
        )
        dest = OUT_DIR / clipped
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(STATIC_SRC / "images" / "boxplot" / ("%s.jpeg" % col), dest)

    print("\nCopying static files:")
    copy_static()
    print("  %d files" % len(copied_static))

    # Stops GitHub Pages running the files through Jekyll.
    (OUT_DIR / ".nojekyll").write_text("", encoding="utf-8")

    if created:
        user.delete()

    total = sum(f.stat().st_size for f in OUT_DIR.rglob("*") if f.is_file())
    print("\nBuilt %s (%.1f KB)" % (OUT_DIR, total / 1024))


if __name__ == "__main__":
    main()
