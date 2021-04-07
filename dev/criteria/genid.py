import util.math as math


def generate_id(text: str) -> str:
    """
    Beware that the text is 1: blank and period stripped and lowerised...So it is case insensitive, since
    what is important is that the content of the text is matched, regardless of it form.
    :param text: the text to hash
    :return: the md5-hashed text
    """
    return math.hash(text.strip().strip('.').lower())
