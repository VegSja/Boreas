import os as _os

_PKG_ROOT = _os.path.dirname(_os.path.abspath(__file__))
_os.environ["DLT_CONFIG_DIR"] = _os.path.join(_PKG_ROOT, ".dlt")
_os.environ["DLT_PROJECT_DIR"] = _PKG_ROOT
