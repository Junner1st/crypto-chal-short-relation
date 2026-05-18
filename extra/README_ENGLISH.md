# Short Relation

## Challenge Design

Compared with [Φ2Sin](https://github.com/Junner1st/crypto-chal-phi-2-sin), this challenge increases the record $\texttt{window}$ to $2^{48}$.

Let's look at the challenge:

---

The service runs on the $j = 0$ curve

$$
E / \mathbb{F}_p: y^2 = x^3 - 17,\quad p = 2^{127} - 1
$$

The record relation is

$$
x = m \cdot \texttt{window} + k
$$

and it must satisfy

$$
0 \le m < \texttt{item\\_limit},\quad 0 \le k < \texttt{window}
$$

$$
y \equiv z^2 \pmod p,\quad (x, y) \in E(\mathbb{F}_p)
$$

The density of valid $x_1$ values is about $2^{-15}$, so we can brute-force until we find a bounded modular short relation.

$$\begin{align*}
& a\cdot x_1 = a \cdot (m_1 \cdot \texttt{window} + k_1) \equiv \texttt{account\\_id} \cdot \texttt{window} + k_2 \pmod p \\
\implies & x_1 \equiv a^{-1} \cdot (\texttt{account\\_id} \cdot \texttt{window} + k_2) \pmod p
\end{align*}
$$

As long as $x_1$ falls within the valid record range

$$
0 \le x_1 < \texttt{item\\_limit} \cdot \texttt{window}
$$

it can pass the record relation check for $x = m \cdot \texttt{window} + k$.

So where does $2^{-15}$ come from?

We have

$$
p = 2^{127}-1 \approx 2^{127},\quad
\texttt{item\\_limit} \cdot \texttt{window} = 2^{64} \cdot 2^{48} = 2^{112}
$$

When trying a random $k_2$, the probability that $x_1$ falls within the valid range is approximately

$$
\frac{2^{112}}{2^{127}} = 2^{-15}
$$

Therefore, the expected number of attempts is $2^{15}$. After adding the constant factors from the curve point check and the $y = z^2$ witness, we can still find a usable relation quickly.

After finding this short relation, we have $x_2 \equiv a x_1 \pmod p$. We can use the public order-3 automorphism $\phi(x, y) = (a x, y)$ on the curve to transport the signature, where $a^3 = 1,\ a \ne 1$.

Because scalar multiplication commutes with $\phi$, the signature on the non-reserved account ($x_1$) can be transported to the reserved account ($x_2$).


## Exploit Flow

1. Call $\texttt{params}$ to get $p$, $b$, $\texttt{window}$, $\texttt{item\\_limit}$, $\texttt{account\\_id}$, and the automorphism coefficient $a$.
2. Compute $a^{-1}$, and set $\texttt{base} = a^{-1} \cdot \texttt{account\\_id} \cdot \texttt{window} \bmod p$.
3. Enumerate from $k_2 = 0$, computing $x_1 = \texttt{base} + a^{-1} \cdot k_2 \bmod p$.
4. Check whether $x_1 < \texttt{item\\_limit} \cdot \texttt{window}$; if true, split it into $m_1, k_1 = \mathrm{divmod}(x_1, \texttt{window})$.
5. Check that $m_1$ is not the reserved account, and verify $a \cdot x_1 \equiv \texttt{account\\_id} \cdot \texttt{window} + k_2 \pmod p$.
6. Check that the corresponding curve point exists, and that witness $z$ satisfies $y \equiv z^2 \pmod p$.
7. Ask the oracle to sign the non-reserved relation point $(x_1, y)$.
8. Apply the automorphism to the returned token: multiply the token's x-coordinate by $a$, keep the y-coordinate unchanged, namely $(s_x, s_y) \mapsto (a \cdot s_x, s_y)$.
9. Submit the transported token to verify the reserved account point $(x_2, y)$ and get the flag.

[solver script is here](/extra/solve.py)

## FLAG

`CCCTF{walkFAAtHHur_u_bec0me_gIant}`
