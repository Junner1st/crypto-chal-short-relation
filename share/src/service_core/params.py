from __future__ import annotations

import os

P_FIELD = 2**127 - 1
B_CURVE = (-17) % P_FIELD

WINDOW = 2**48
ITEM_LIMIT = 2**64

ACCOUNT_NAME = b"admin"
ACCOUNT_ID = 14390906360933683949

FLAG = os.environ.get("FLAG", "flag{test}")
