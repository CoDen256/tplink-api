def check(param, param_type, name):
    if not isinstance(param, param_type):
        raise AttributeError(f"{name} should be {param_type}, but was: {type(param)}| Value: {param}")
    return param


def multiply(x, y):
    return [a * b for a, b in zip(x, y)]

