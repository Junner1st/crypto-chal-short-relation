from __future__ import annotations

import json
from pwn import context, remote


HOST = "127.0.0.1"
PORT = 1341

context.log_level = "error"

M1 = 8146028315705618244
K1 = 152412937362079
K2 = 32177714059992
Y = 25363445879608729728248549883740991412
Z = 108262469077901162367789937632640773108


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


def main() -> None:
    client = Client(HOST, PORT)
    try:
        params = client.call("params")
        assert params["ok"], params

        p = params["p"]
        window = params["window"]
        account_id = params["account_id"]
        a = params["a"]

        x1 = M1 * window + K1
        x2 = account_id * window + K2
        assert (a * x1 - x2) % p == 0

        sign_resp = client.call(
            "sign",
            {
                "m": M1,
                "x": x1,
                "y": Y,
                "k": K1,
                "z": Z,
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
                "y": Y,
                "k": K2,
                "z": Z,
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
