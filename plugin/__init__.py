import os, sys

path = os.path.dirname(os.path.abspath(__file__))

for py in [
    f[:-3] for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"
]:
    mod = __import__(".".join([__name__, py]), fromlist=[py])
    plugins = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]
    for plugin in plugins:
        setattr(sys.modules[__name__], plugin.__name__, plugin)
