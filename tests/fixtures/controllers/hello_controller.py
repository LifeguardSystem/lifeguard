from lifeguard.controllers import controller


@controller("/hello")
def hello():
    return "hello"
