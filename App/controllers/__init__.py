from types import ModuleType
from typing import List
import importlib
import pkgutil

from . import user as _user
from . import auth as _auth
from . import resident as _resident
from . import driver as _driver
from . import initialize as _initialize
from . import admin as _admin

_SUBMODULES: List[ModuleType] = [
    _user, _auth, _resident, _driver, _initialize, _admin
]

def _find_attr_in_submodules(name: str):
    for mod in _SUBMODULES:
        if hasattr(mod, name):
            return getattr(mod, name)
    return None

def __getattr__(name: str):
    attr = _find_attr_in_submodules(name)
    if attr is not None:
        return attr
    mod_names = ", ".join(m.__name__ for m in _SUBMODULES)
    raise AttributeError(
        f"module 'App.controllers' has no attribute '{name}'. "
        f"Searched submodules: {mod_names}"
    )

def __dir__():
    attrs = set()
    for mod in _SUBMODULES:
        try:
            for a in dir(mod):
                attrs.add(a)
        except Exception:
            continue
    attrs.update(globals().keys())
    return sorted(attrs)
