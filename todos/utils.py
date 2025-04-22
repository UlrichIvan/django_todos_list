import uuid
import random


def get_code() -> str:
    code_long = "".join(str(uuid.uuid4()).split("-"))
    code = code_long[0 : random.randint(8, 10)]
    return code.upper()
