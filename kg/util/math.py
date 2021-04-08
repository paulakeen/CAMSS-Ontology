import hashlib


def inc(n: int) -> int:
    n += 1
    return n


def dec(n: int) -> int:
    n -= 1
    return n


def hash(text: str) -> str:
    if text:
        return hashlib.md5(text.encode()).hexdigest()
    else:
        raise Exception("No md5-based id generated because no thruty provided.")


def md5(text: str) -> str:
    if text:
        return hashlib.md5(text.encode()).hexdigest()
    else:
        raise Exception("No md5-based id generated because no thruty provided.")


def sha256(text: str) -> str:
    if text:
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise Exception("No sha256-based id generated because no thruty provided.")

