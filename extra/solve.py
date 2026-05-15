from __future__ import annotations

import json
from pwn import context, remote


HOST = "127.0.0.1"
PORT = "1341"

context.log_level = "error"


class Client:
    def __init__(self, host: str, port: int):
        self.io = remote(host, port)
        self.io.recvuntil(b"> ")

    def close(self) -> None:
        self.io.sendline(b"exit")
        self.io.close()

    def call(self, cmd: str, payload: dict | None = None) -> dict:
        if payload is None:
            line = cmd
        else:
            line = f"{cmd} {json.dumps(payload, separators=(',', ':'))}"

        self.io.sendline(line.encode())
        data = self.io.recvuntil(b"> ", drop=True).strip()
        return json.loads(data.splitlines()[-1])


def is_square(x: int, p: int) -> bool:
    x %= p
    if x == 0:
        return True
    return pow(x, (p - 1) // 2, p) == 1


def sqrt_mod(x: int, p: int) -> int:
    x %= p
    if x == 0:
        return 0

    # The first Short Relation challenge uses p = 2^127 - 1, so p % 4 == 3.
    if p % 4 != 3:
        raise ValueError("this simple solver expects p % 4 == 3")

    y = pow(x, (p + 1) // 4, p)
    if (y * y) % p != x:
        raise ValueError("not a square")
    return y


def find_witness(p: int, b: int, x: int) -> tuple[int, int]:
    rhs = (pow(x, 3, p) + b) % p
    y = sqrt_mod(rhs, p)

    if not is_square(y, p):
        y = (-y) % p

    z = sqrt_mod(y, p)
    return int(y), int(z)


def find_relation(params: dict) -> tuple[int, int, int, int, int, int]:
    p = int(params["p"])
    b = int(params["b"])
    window = int(params["window"])
    item_limit = int(params["item_limit"])
    account_id = int(params["account_id"])
    a = int(params["a"])

    bound = item_limit * window
    ainv = pow(a, -1, p)
    base = (ainv * account_id * window) % p

    for k2 in range(window):
        x1 = (base + ainv * k2) % p
        if x1 >= bound:
            continue

        m1, k1 = divmod(x1, window)
        if m1 == account_id:
            continue
        if not (0 <= m1 < item_limit and 0 <= k1 < window):
            continue

        x2 = account_id * window + k2
        if (a * x1 - x2) % p != 0:
            continue

        try:
            y, z = find_witness(p, b, x1)
        except ValueError:
            continue

        return int(m1), int(k1), int(k2), int(x1), int(y), int(z)

    raise RuntimeError("short relation not found")


def main() -> None:
    client = Client(HOST, PORT)
    try:
        params = client.call("params")
        assert params["ok"], params

        p = params["p"]
        window = params["window"]
        account_id = params["account_id"]
        a = params["a"]
        m1, k1, k2, x1, y, z = find_relation(params)

        x2 = account_id * window + k2
        assert (a * x1 - x2) % p == 0

        sign_resp = client.call(
            "sign",
            {
                "m": m1,
                "x": x1,
                "y": y,
                "k": k1,
                "z": z,
            },
        )
        assert sign_resp.get("ok"), sign_resp

        token = sign_resp["token"]
        token2 = {
            "x": (a * token["x"]) % p,
            "y": token["y"],
        }

        verify_resp = client.call(
            "verify",
            {
                "x": x2,
                "y": y,
                "k": k2,
                "z": z,
                "sx": token2["x"],
                "sy": token2["y"],
            },
        )
        assert verify_resp.get("ok"), verify_resp
        print(verify_resp["flag"])
    finally:
        client.close()


if __name__ == "__main__":
    main()
