def check(param, param_type, name):
    if not isinstance(param, param_type):
        raise AttributeError(f"{name} should be {param_type}, but was: {type(param)}| Value: {param}")
    return param


def multiply(x, y):
    return [a * b for a, b in zip(x, y)]


def iptonum(ip):
    parts = ip.split(".")
    result = 0
    for part in parts:
        result = (result << 8) + int(part)
    return result

def partition(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield tuple(lst[i:i + n])