import importlib
import inspect
import pkgutil

from .base import Rule


def discover_rules():
    seen = set()
    rules = []

    package = importlib.import_module("rules")

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name in {"base", "engine", "registry"}:
            continue

        module = importlib.import_module(f"rules.{module_name}")

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Rule) and cls is not Rule:
                key = (cls.__module__, cls.__name__)

                if key not in seen:
                    seen.add(key)
                    rules.append(cls)

    return rules
