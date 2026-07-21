# Transcription audit: Proposition 4.3 to the certified systems

## Status of this document

This audit separates three logically different statements:

1. **Published input.** Guccione--Guccione--Horruitiner--Valqui (GGHV)
   reduce the unresolved `(72,108)` degree pair to the two Laurent/Newton
   configurations in their Proposition 4.3.
2. **Local transcription.** The two polygons and the equation `[P,Q]=x^2`
   are converted into the coefficient systems archived in the frozen
   `v1.0.1` replay.
3. **Exact certificates.** The archived verifiers check explicit
   characteristic-zero identities for those coefficient systems.

The present repository now machine-checks items 2 and 3. It does **not**
re-prove the upstream arguments establishing Proposition 4.3, and no external
specialist has yet signed off on the transcription. The public claim therefore
remains an exact candidate exclusion conditional on the published reduction.

## Frozen sources

| Object | Permanent location | SHA-256 |
|---|---|---|
| GGHV arXiv v1 PDF | <https://arxiv.org/pdf/2204.14178> | `ac18e80cc2391f204f73b908a6a6557eb1141d9fbb5ebdb9f6e0a22121db80bd` |
| GGHV arXiv v1 TeX source | <https://arxiv.org/e-print/2204.14178> | `cac83f92efca63de3da6ca811b9837061e1a343a44b8039c8748d1b72423cba7` |
| Frozen repository snapshot | <https://doi.org/10.5281/zenodo.21479814> | `f7f0876de12d35badbed2be6a773d4a9dada50aff778c080126aab541deefcde` |
| Nested exact replay ZIP | inside the Zenodo snapshot | `232204bdb598cc2ea0368e154c8573e18bbfdc69fa631c8878de4b884b38bb18` |

The page references below are PDF page numbers in arXiv v1.

## Published statements used

| Published statement | Location | Local use | Audit status |
|---|---|---|---|
| Below maximum degree `125`, a counterexample either has maximum degree at least `125` or degree pair `(72,108)` / `(108,72)`. | Theorem 2.1, p. 2 | Converts exclusion of `(72,108)` into the conditional degree-`125` bound. | Text checked against the PDF and TeX source. Upstream classification not re-proved. |
| The `(8,28)` case yields `P,Q in L^(1)` with `[P,Q]=x^2` and one of two stated Newton-polygon pairs. | Proposition 4.3, pp. 10--12 | Starting point of both certified systems. | Statement checked character-for-character at the level of vertices, ring and bracket. |
| Cases (a),(b) become the four-vertex pair; case (c) becomes the five-vertex pair under the final morphism. | Proof of Proposition 4.3, p. 12 | Confirms that the two listed alternatives are exhaustive within the proposition. | Text checked. Correctness of the proof and its cited predecessors remains an external mathematical input. |

The vertices transcribed locally are exactly:

```text
Case 1:
N(P)={(0,0),(1,0),(8,14),(8,16),(0,8)}
N(Q)={(0,0),(2,1),(12,21),(12,24),(0,12)}

Case 2:
N(P)={(0,0),(1,0),(8,14),(8,16)}
N(Q)={(0,0),(2,1),(12,21),(12,24)}
```

## Coordinate transcription

Set

```text
t = x*y^2,  z = y^(-1).
```

Then `x^i y^j = t^i z^(2i-j)`, `[t,z]_(x,y)=-1`, and
`x^2=t^2 z^4`. Direct lattice enumeration gives:

| Polygon | Lattice points | `z`-bands |
|---|---:|---|
| Case 1, `P` | 61 | `-8,...,2` |
| Case 1, `Q` | 125 | `-12,...,3` |
| Case 2, `P` | 25 | `0,1,2` |
| Case 2, `Q` | 47 | `0,1,2,3` |

Thus the full Case 2 ansatz is

```text
P=A(t)z^2+B(t)z+C(t),
Q=D(t)z^3+E(t)z^2+F(t)z+G(t).
```

Case 1 contains the same upper bands and the additional negative bands listed
above. `verify_transcription_bridge.py` independently recomputes all four
lattice sets and the band ranges. It does not trust saved point lists.

Constants of `P` and `Q` are set to zero by subtracting constants. This does
not change the Jacobian bracket. It may remove `(0,0)` from the support of the
translated pair, but every pair with the published polygons maps to a pair in
the implemented ansatz, which is the direction required for an exclusion.

## Vertex normalization

Let `a1`, `a8`, and `c8` be the nonzero coefficients of `P` at `(1,0)`,
`(8,14)`, and `(8,16)`. For

```text
P~ = rho P(lambda*x,mu*y),
Q~ = sigma Q(lambda*x,mu*y),
```

choose nonzero constants satisfying

```text
mu^2     = a8/c8,
lambda^7 = (a1/a8) mu^(-14),
rho      = (a1 lambda)^(-1),
sigma    = (rho lambda^3 mu)^(-1).
```

Over the algebraically closed characteristic-zero ground field, the required
roots exist. The three vertex coefficients of `P~` are exactly one, while

```text
[P~,Q~] = rho sigma lambda^3 mu x^2 = x^2.
```

This justifies the implemented assignments `a1=a8=c8=1`. The identities are
checked symbolically by `verify_transcription_bridge.py`; no coefficient of
`Q` is normalized independently.

## The five coefficient equations

Equating powers of `z` in `[P,Q]=x^2` gives:

```text
(J4) 2AD' - 3A'D = t^2
(J3) 2(AE'-A'E) + (BD'-3B'D) = 0
(J2) (2AF'-A'F) + (BE'-2B'E) - 3C'D = 0
(J1) 2AG' + (BF'-B'F) - 2C'E = 0
(J0) BG' - C'F = 0
```

The sign convention follows from `[t,z]=-1`. Both
`verify_laurent_reduction.py` in the frozen replay and the new bridge verifier
differentiate the generic ansatz symbolically and compare every coefficient.

## First block and coefficient field

The normalized top bands are

```text
A=t+a2*t^2+...+a7*t^7+t^8,
D=d2*t^2+...+d12*t^12.
```

The supports follow from the two polygon vertices on the `z^2` and `z^3`
bands. Exact triangular elimination in `(J4)` solves all 11 coefficients of
`D` and leaves six equations in `a2,...,a7`. The saved rational lexicographic
basis consists of one degree-35 irreducible equation in `a7` and five equations
linear in `a2,...,a6`.

`verify_firstblock_exact.py` checks the triangular substitutions, reduces all
six original residuals by the saved lex basis, and verifies irreducibility over
the rationals. Because the degree-35 polynomial is irreducible, all its roots
are conjugate; an exact identity in the quotient field transports to every
embedding into an algebraic closure.

## Case 2 coverage

All lattice-supported coefficients of `B,C,E,F,G` are present; only the two
removable constants are omitted. Exact linear elimination solves `(J3)` and
`(J2)`, after which `(J1)` and `(J0)` produce 25 compatibility equations in
three parameters. The serialized certificate uses four regenerated equations
and verifies

```text
1 = sum(T_i R_i).
```

The verifier compares the saved generators with fresh exact regeneration
before evaluating the identity. Therefore a certificate for a different
system cannot pass silently.

## Case 1 coverage and exhaustive reductions

### Descending bands

Starting from the common upper bands, the generator introduces the complete
lattice slices needed for bracket layers `z^1,z^0,z^-1,z^-2,z^-3`. It obtains
13 compatibility equations in six parameters. A hypothetical full Case 1
pair must satisfy these layers, so inconsistency of this necessary subsystem is
sufficient; lower layers need not be added to prove nonexistence.

The bridge verifier checks the expected layer labels

```text
0,0,-1,-1,-2,-2,-2,-2,-3,-3,-3,-3,-3
```

and regenerates both seven-equation pre-division branch systems from the saved
13 equations.

### Exhaustive sign split

The first compatibility equation is checked directly in the degree-35 field
to have the exact form

```text
kappa (s^2-c^2)^2,
```

with `kappa != 0` and `c != 0`. The two archived branch values are checked to
be `c` and `-c`. Hence every common zero belongs to one of the two branches;
this is not a finite-field inference.

### Elimination of `r`

On each branch the verifier reconstructs

```text
E6-lambda*E2 = S*L^2
```

with `lambda,S` nonzero field constants and `L` affine-linear with coefficient
one on `r`. In a characteristic-zero field a common zero therefore has `L=0`.
The substitution is an invertible affine elimination, not division by a
parameter polynomial. Every discarded surviving equation is checked to be an
exact nonzero field-scalar multiple of a retained equation.

### Change of `h`, `h=0`, and `h!=0`

The affine translation of `h` has coefficient one and is invertible. It yields
seven pre-division equations in `(h,u1,u2,u3)`. Their first equation has the
checked form

```text
nonzero_constant * (h*u3-N(h,u1,u2)).
```

For `h!=0`, substituting `u3=N/h` and clearing powers of `h` produces the six
archived equations. The verifier reconstructs those equations term by term.
The current data have no additional common factor of `h` to divide out (the
recorded minimum powers are all zero), but the logical split remains explicit.

For `h=0`, two unit certificates are evaluated against the original
seven-equation pre-division systems. Their payloads include the SHA-256 of
those source systems. Thus the `h=0` component is not discarded by saturation.

For `h!=0`, the hard exact identity

```text
h = sum(T_i E_i)
```

forces `h=0`, a contradiction. The exact involution transporting the second
sign branch is checked coefficient by coefficient.

## Division and saturation ledger

| Operation | Inverted object | Why no component is lost |
|---|---|---|
| Vertex normalization | nonzero vertex coefficients and torus scalars | Nonzero by definition of the listed vertices; the ground field supplies the required roots. |
| Linear solves | pivots in the exact number field | Every pivot is asserted nonzero; these are constants, not parameter polynomials. Compatibility rows are retained as equations. |
| `r` elimination | nonzero field constants; monic affine variable change | The exact square forces the affine form to zero at every common zero. |
| Proportional-equation removal | nonzero field constants | Removed equations have exactly the same zero set as retained equations. |
| `h` translation | coefficient one | Polynomial automorphism. |
| `u3=N/h` | `h`, only in the declared `h!=0` branch | The complementary `h=0` branch is checked on the original pre-division equations by separate unit certificates. |
| Degree-35 to degree-5 descent | exact field embedding and nonzero graded rescaling | Both branch systems are regenerated, then the degree-five symmetry and hard identities are checked exactly. |

No localization by an unrecorded parameter polynomial was found.

## Machine audit commands

From a checked-out `v1.1` audit branch:

```bash
docker build -t jc2-exact-audit .
docker run --rm jc2-exact-audit
```

The image downloads `v1.0.1` from Zenodo only, verifies both archive hashes,
runs the frozen replay, runs this bridge audit, and then runs five deliberate
corruption tests. The final marker is:

```text
JC2_72_108_CLEAN_ROOM_PASS
```

## Remaining external audit questions

The following questions are intentionally left open for independent review:

1. Is the proof of GGHV Proposition 4.3, including every cited predecessor,
   correct and exhaustive for the `(8,28)` case?
2. Are the conventions for the algebraically closed characteristic-zero ground
   field and `L^(1)` being used exactly as intended by GGHV?
3. Does an independent Jacobian-conjecture specialist agree that constant
   subtraction and the three-coefficient torus normalization preserve the
   implication needed for exclusion?
4. Can a second computer-algebra implementation replay the identities without
   importing the supplied polynomial-arithmetic code?

Until questions 1--3 receive external confirmation, the degree-`125`
consequence should remain explicitly conditional.
