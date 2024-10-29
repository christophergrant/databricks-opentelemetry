import time
import random


def uuid7():
    # Step 1: Get Unix timestamp in milliseconds
    unix_ts_ms = int(time.time() * 1000)  # 48-bit timestamp

    # Step 2: Generate random bits for rand_a (12 bits) and rand_b (62 bits)
    rand_a = random.getrandbits(12)
    rand_b = random.getrandbits(62)

    # Step 3: Pack the parts into a 128-bit structure
    # 48-bit timestamp, 4-bit version, 12-bit rand_a, 2-bit variant, 62-bit rand_b
    uuid_int = (
        (unix_ts_ms << 80) | (0b0111 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    )

    # Convert to hex and format as UUID
    uuid_hex = f"{uuid_int:032x}"
    uuid_formatted = f"{uuid_hex[:8]}-{uuid_hex[8:12]}-{uuid_hex[12:16]}-{uuid_hex[16:20]}-{uuid_hex[20:]}"

    return uuid_formatted
