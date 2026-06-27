import importlib.util
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
DJANGO_WSGI = BACKEND_DIR / "config" / "wsgi.py"
CPANEL_SITE_PACKAGES = Path("/home/cloudeu2/virtualenv/lms/3.12/lib/python3.12/site-packages")

for path in (BACKEND_DIR, PROJECT_ROOT, CPANEL_SITE_PACKAGES):
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("PYTHON_EGG_CACHE", str(PROJECT_ROOT / ".python-eggs"))

spec = importlib.util.spec_from_file_location("cloudeuz_django_wsgi", DJANGO_WSGI)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load Django WSGI module from {DJANGO_WSGI}")

django_wsgi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(django_wsgi)
application = django_wsgi.application
