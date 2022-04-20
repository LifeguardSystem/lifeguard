from lifeguard.controllers import controller


@controller("/subdir")
def subdir():
    return "hello"
