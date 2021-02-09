def set_function_attributes(**kwargs):
    def decorator(func):
        for key, val in kwargs.items():
            setattr(func, key, val)

        return func

    return decorator


def normalize_townname(townname):
    return townname.replace("台", "臺")
