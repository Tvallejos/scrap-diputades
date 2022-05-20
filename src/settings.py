import logging

def init():
    fmt = "[ %(funcName)0s() ] %(message)s"
    logging.basicConfig(level=logging.INFO,format=fmt)
    return
