# Short Relation

## Challenge Design

Compared with [Phi2Sin](https://github.com/Junner1st/crypto-chal-phi-2-sin),
this challenge increases the record $\texttt{window}$ to $2^{48}$.

Let's look at the challenge.

---

The service works over the $j = 0$ curve

$$
E / \mathbb{F}_p: y^2 = x^3 - 17,\quad p = 2^{127} - 1
$$

The record relation is

$$
x = m \cdot \texttt{window} + k
$$

and it must satisfy

$$
0 \le m < \texttt{item\_limit},\quad 0 \le k < \texttt{window}
$$

$$
y \equiv z^2 \pmod p,\quad (x, y) \in E(\mathbb{F}_p)
$$

The density of valid $x_1$ values is about $2^{-15}$, so we can brute force
until we find a bounded modular short relation.

$$\begin{align*}
& a\cdot x_1 = a \cdot (m_1 \cdot \texttt{window} + k_1) \equiv \texttt{account\_id} \cdot \texttt{window} + k_2 \pmod p \\
\implies & x_1 \equiv a^{-1} \cdot (\texttt{account\_id} \cdot \texttt{window} + k_2) \pmod p
\end{align*}
$$

As long as $x_1$ falls into the valid record range

$$
0 \le x_1 < \texttt{item\_limit} \cdot \texttt{window}
$$

it passes the record relation check $x = m \cdot \texttt{window} + k$.

Where does $2^{-15}$ come from?

We have

$$
p = 2^{127}-1 \approx 2^{127},\quad
\texttt{item\_limit} \cdot \texttt{window} = 2^{64} \cdot 2^{48} = 2^{112}
$$

When trying a random $k_2$, the probability that $x_1$ falls into the valid
range is approximately

$$
\frac{2^{112}}{2^{127}} = 2^{-15}
$$

So the expected number of attempts is $2^{15}$.  Even after multiplying by the
constant factors from the curve-point check and the $y = z^2$ witness condition,
we can still find a usable relation quickly.

After finding this short relation, we have $x_2 \equiv a x_1 \pmod p$.  We can
then transport the signature using the public order-3 automorphism
$\phi(x, y) = (a x, y)$ on the curve, where $a^3 = 1,\ a \ne 1$.

Because scalar multiplication commutes with $\phi$, a signature on the
non-reserved account ($x_1$) can be transported to the reserved account ($x_2$).

## Exploit Process

1. Request `params` to get `p`, `b`, `window`, `item_limit`, `account_id`, and the automorphism coefficient `a`.
2. Compute `a^-1`, and set `base = a^-1 * account_id * window mod p`.
3. Enumerate from `k2 = 0`, computing `x1 = base + a^-1 * k2 mod p`.
4. Check whether `x1 < item_limit * window`; if so, split it with `m1, k1 = divmod(x1, window)`.
5. Check that `m1` is not the reserved account, and verify `a*x1 == account_id*window + k2 (mod p)`.
6. Check that the corresponding curve point exists and that witness `z` satisfies `y = z^2 mod p`.
7. Ask the oracle to sign the non-reserved relation point `(x1, y)`.
8. Push the returned token forward with the automorphism, giving `(a*sx, sy)`.
9. Submit the transported token for the reserved account point `(x2, y)` to get the flag.

[solver script is here](/extra/solve.py)

## FLAG

`CCCTF{walkFAAtHHur_u_bec0me_gIant}`
