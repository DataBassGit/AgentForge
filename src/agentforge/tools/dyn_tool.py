def action(tool, payload, func="run"):
    import importlib
    module = importlib.import_module(tool)
    run = getattr(module, func)
    result = run(payload)
    return result
