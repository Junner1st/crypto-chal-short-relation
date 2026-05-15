# Short Relation

## 題目設計

相比於 [Φ2Sin](https://github.com/Junner1st/crypto-chal-phi-2-sin)，這題 record 的 $\texttt{window}$ 放大為 $2^{48}$。

來看題目內容：

---

服務在 $j = 0$ 曲線上運作

$$
E / \mathbb{F}_p: y^2 = x^3 - 17,\quad p = 2^{127} - 1
$$

record relation 為

$$
x = m \cdot \texttt{window} + k
$$

並且需要滿足

$$
0 \le m < \texttt{item\\_limit},\quad 0 \le k < \texttt{window}
$$

$$
y \equiv z^2 \pmod p,\quad (x, y) \in E(\mathbb{F}_p)
$$

合法 $x_1$ 的密度大約是 $2^{-15}$ ，可以暴力列舉直到找到一組 bounded modular short relation。

$$\begin{align*}
& a\cdot x_1 = a \cdot (m_1 \cdot \texttt{window} + k_1) \equiv \texttt{account\\_id} \cdot \texttt{window} + k_2 \pmod p \\
\implies & x_1 \equiv a^{-1} \cdot (\texttt{account\\_id} \cdot \texttt{window} + k_2) \pmod p
\end{align*}
$$

只要 $x_1$ 落在合法 record 範圍

$$
0 \le x_1 < \texttt{item\\_limit} \cdot \texttt{window}
$$

就能通過 record relation 的 $x = m \cdot \texttt{window} + k$ 的檢查。

至於 $2^{-15}$ 是怎麼算的呢？

有

$$
p = 2^{127}-1 \approx 2^{127},\quad
\texttt{item\\_limit} \cdot \texttt{window} = 2^{64} \cdot 2^{48} = 2^{112}
$$

隨機嘗試一個 $k_2$ 時，$x_1$ 落在合法範圍的機率約為

$$
\frac{2^{112}}{2^{127}} = 2^{-15}
$$

所以期望嘗試次數為 $2^{15}$，再加上曲線點與 $y = z^2$ witness 的常數因子，可以很快找到可用 relation。

找到這組 short relation 後，就有 $x_2 \equiv a x_1 \pmod p$。可以利用曲線上的公開三階自同態 $\phi(x, y) = (a x, y)$ 搬運簽章，其中 $a^3 = 1,\ a \ne 1$。

因為純量乘法會和 $\phi$ 交換，非 reserved account ($x_1$) 上的簽章可以被搬運到 reserved account ($x_2$) 上。


## 攻擊流程

1. 呼叫 `params` 取得 `p`、`b`、`window`、`item_limit`、`account_id` 和自同態係數 `a`。
2. 計算 `a^-1`，並令 `base = a^-1 * account_id * window mod p`。
3. 從 `k2 = 0` 開始枚舉，計算 `x1 = base + a^-1 * k2 mod p`。
4. 檢查 `x1 < item_limit * window`，若成立就拆成 `m1, k1 = divmod(x1, window)`。
5. 檢查 `m1` 不是 reserved account，並確認 `a*x1 == account_id*window + k2 (mod p)`。
6. 檢查對應曲線點是否存在，並確認 witness `z` 讓 `y = z^2 mod p`。
7. 請 oracle 對非 reserved 的 relation point `(x1, y)` 簽章。
8. 對回傳 token 套用自同態，得到 `(a*sx, sy)`。
9. 把搬運後的 token 送去驗證 reserved account 的點 `(x2, y)`，取得 flag。

[solver script is here](/extra/solve.py)

## FLAG

`CCCTF{walkFAAtHHur_u_bec0me_gIant}`
