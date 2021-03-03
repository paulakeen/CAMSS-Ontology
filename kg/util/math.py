import hashlib


def inc(n: int) -> int:
    n += 1
    return n


def dec(n: int) -> int:
    n -= 1
    return n


def hash(text: str) -> str:
    if text:
        md5 = hashlib.md5(text.encode()).hexdigest()
    else:
        raise Exception("No md5-based id generated because no thruty provided.")
    return md5
