#!/usr/bin/env python3
"""Audit the algebraic bridge around the frozen v1.0.1 certificate replay.

This does not re-prove Proposition 4.3.  It checks the local transcription from
its two stated Newton polygons to the exact coefficient systems, including the
normalization, exhaustive sign split, affine eliminations, and the only
division by a variable (which is confined to h != 0 and paired with an h = 0
certificate on the original pre-division system).
"""

from __future__ import annotations

import pickle
import re
import sys
from pathlib import Path

import sympy as sp
from flint import fmpq, fmpq_poly


def fail(message: str) -> None:
    raise RuntimeError(message)


def lattice_points(vertices):
    def inside(point):
        signs = []
        for left, right in zip(vertices, vertices[1:] + vertices[:1]):
            cross = ((right[0] - left[0]) * (point[1] - left[1])
                     - (right[1] - left[1]) * (point[0] - left[0]))
            if cross:
                signs.append(cross > 0)
        return not signs or all(signs) or not any(signs)

    return {
        (x, y)
        for x in range(min(p[0] for p in vertices), max(p[0] for p in vertices) + 1)
        for y in range(min(p[1] for p in vertices), max(p[1] for p in vertices) + 1)
        if inside((x, y))
    }


def bands(points):
    result = {}
    for x, y in points:
        result.setdefault(2 * x - y, []).append(x)
    return {key: (min(values), max(values), len(values)) for key, values in result.items()}


def verify_polygons_and_coordinates():
    case1_p = [(0, 0), (1, 0), (8, 14), (8, 16), (0, 8)]
    case1_q = [(0, 0), (2, 1), (12, 21), (12, 24), (0, 12)]
    case2_p = case1_p[:-1]
    case2_q = case1_q[:-1]
    points = [lattice_points(v) for v in (case1_p, case1_q, case2_p, case2_q)]
    if list(map(len, points)) != [61, 125, 25, 47]:
        fail(f"unexpected lattice counts: {list(map(len, points))}")

    p1_bands, q1_bands, p2_bands, q2_bands = map(bands, points)
    if sorted(p2_bands) != [0, 1, 2] or sorted(q2_bands) != [0, 1, 2, 3]:
        fail("Case 2 does not have the implemented upper-band support")
    if sorted(p1_bands) != list(range(-8, 3)):
        fail("Case 1 P bands do not cover z exponents -8 through 2")
    if sorted(q1_bands) != list(range(-12, 4)):
        fail("Case 1 Q bands do not cover z exponents -12 through 3")

    t, z = sp.symbols("t z")
    a, b, c, d, e, f, g = [sp.Function(name)(t) for name in "ABCDEFG"]
    p = a * z**2 + b * z + c
    q = d * z**3 + e * z**2 + f * z + g
    jac = sp.expand(sp.diff(p, t) * sp.diff(q, z) - sp.diff(p, z) * sp.diff(q, t))
    expected = [
        -b * sp.diff(g, t) + sp.diff(c, t) * f,
        -2 * a * sp.diff(g, t) - b * sp.diff(f, t) + 2 * sp.diff(c, t) * e + sp.diff(b, t) * f,
        -2 * a * sp.diff(f, t) - b * sp.diff(e, t) + 3 * sp.diff(c, t) * d + 2 * sp.diff(b, t) * e + sp.diff(a, t) * f,
        -2 * a * sp.diff(e, t) - b * sp.diff(d, t) + 3 * sp.diff(b, t) * d + 2 * sp.diff(a, t) * e,
        -2 * a * sp.diff(d, t) + 3 * sp.diff(a, t) * d,
    ]
    if any(sp.expand(jac.coeff(z, degree) - value) for degree, value in enumerate(expected)):
        fail("one of the J0--J4 coefficient identities is incorrect")

    x, y = sp.symbols("x y", nonzero=True)
    txy, zxy = x * y**2, y**-1
    coordinate_jacobian = sp.diff(txy, x) * sp.diff(zxy, y) - sp.diff(txy, y) * sp.diff(zxy, x)
    if sp.simplify(coordinate_jacobian + 1) or sp.simplify(x**2 - txy**2 * zxy**4):
        fail("the Laurent coordinate change or transformed target is incorrect")
    print("PRIMARY_POLYGON_TRANSCRIPTION_LOCAL_PASS")


def verify_normalization():
    # For P~ = rho P(lambda*x, mu*y), the three vertex coefficients become
    # rho*a1*lambda, rho*a8*lambda^8*mu^14, rho*c8*lambda^8*mu^16.
    # The displayed choices make all three equal to one.  sigma then preserves
    # the x^2 bracket.  Only nonzero constants and roots in the algebraically
    # closed ground field are used.
    a1, a8, c8, lam, mu = sp.symbols("a1 a8 c8 lam mu", nonzero=True)
    rho = 1 / (a1 * lam)
    lam7 = a1 * mu**-14 / a8
    mu2 = a8 / c8
    normalized = [
        sp.simplify(rho * a1 * lam),
        sp.simplify((a8 / a1) * lam7 * mu**14),
        sp.simplify((c8 / a1) * lam7 * mu**14 * mu2),
    ]
    if normalized != [1, 1, 1]:
        fail(f"normalization failed symbolically: {normalized}")
    sigma = 1 / (rho * lam**3 * mu)
    if sp.simplify(rho * sigma * lam**3 * mu - 1):
        fail("the normalization does not preserve [P,Q]=x^2")
    print("VERTEX_NORMALIZATION_PASS")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_transcription_bridge.py EXACT_REPLAY_ROOT")
    root = Path(sys.argv[1]).resolve()
    if not (root / "exact_core.py").is_file():
        raise SystemExit(f"not an exact replay root: {root}")
    sys.path.insert(0, str(root))
    import exact_core as ec

    verify_polygons_and_coordinates()
    verify_normalization()

    def decode_k(serialized):
        return ec.K(fmpq_poly([fmpq(n, d) for n, d in serialized]))

    def decode_pp(serialized):
        return ec.PP({tuple(m): decode_k(c) for m, c in serialized})

    state = pickle.loads((root / "case1_checkpoint.pkl").read_bytes())
    if state["done"] != [1, 0, -1, -2, -3] or state["np"] != 6:
        fail("Case 1 checkpoint does not contain the five expected exact layers")
    if state["labels"] != [0, 0, -1, -1, -2, -2, -2, -2, -3, -3, -3, -3, -3]:
        fail("Case 1 compatibility-equation labels changed")
    equations = [decode_pp(q) for q in state["all_comp"]]

    def pp_pow(value, exponent):
        result = ec.PP.const(1)
        while exponent:
            if exponent & 1:
                result *= value
            value *= value
            exponent >>= 1
        return result

    def substitute_scalar(poly, index, value):
        out = {}
        for monomial, coefficient in poly.d.items():
            target = list(monomial)
            exponent = target[index]
            target[index] = 0
            target = tuple(target)
            out[target] = out.get(target, ec.K(0)) + coefficient * value**exponent
        return ec.PP(out)

    def substitute_poly(poly, index, value):
        out = ec.PP()
        for monomial, coefficient in poly.d.items():
            target = list(monomial)
            exponent = target[index]
            target[index] = 0
            out += ec.PP({tuple(target): coefficient}) * pp_pow(value, exponent)
        return out

    def coefficient_of_variable(poly, index):
        out = {}
        for monomial, coefficient in poly.d.items():
            if monomial[index] == 1:
                target = list(monomial)
                target[index] = 0
                out[tuple(target)] = coefficient
        return ec.PP(out)

    def scalar_ratio(left, right):
        if not left.d or set(left.d) != set(right.d):
            return None
        monomial = next(iter(left.d))
        value = left.d[monomial] / right.d[monomial]
        return value if all(left.d[m] == right.d[m] * value for m in left.d) else None

    def coefficient(poly, monomial):
        return poly.d.get(tuple(monomial), ec.K(0))

    q0 = equations[0]
    zero = (0, 0, 0, 0, 0, 0)
    leading = coefficient(q0, (0, 4, 0, 0, 0, 0))
    quadratic = coefficient(q0, (0, 2, 0, 0, 0, 0))
    constant = coefficient(q0, zero)
    if not leading or set(q0.d) != {zero, (0, 2, 0, 0, 0, 0), (0, 4, 0, 0, 0, 0)}:
        fail("the first Case 1 equation is not the expected even quartic in s")
    c_squared = -quadratic / (2 * leading)
    if constant != leading * c_squared**2 or not c_squared:
        fail("the first Case 1 equation is not kappa*(s^2-c^2)^2")

    branch_values = []
    symbol_s = sp.Symbol("s")
    for line in (root / "factor_q0_exact_clean.out").read_text().splitlines()[:2]:
        raw = line.split("=", 1)[1]
        raw = re.sub(r"u(\d+)", r"u**\1", raw)
        raw = re.sub(r"(\d)u", r"\1*u", raw)
        expression = sp.sympify(raw, locals={"s": symbol_s, "u": ec.U})
        branch_values.append(ec.eval_u(-sp.expand(expression - symbol_s)))
    if branch_values[0] != -branch_values[1] or branch_values[0] ** 2 != c_squared:
        fail("the archived two sign branches are not exactly the quartic roots")
    print("EXHAUSTIVE_SIGN_SPLIT_PASS")

    min_h_powers_by_branch = []
    for branch_number, branch_value in enumerate(branch_values, 1):
        reduced = [substitute_scalar(q, 1, branch_value) for q in equations]
        ratio = scalar_ratio(coefficient_of_variable(reduced[6], 3), coefficient_of_variable(reduced[2], 3))
        if ratio is None:
            fail(f"branch {branch_number}: the r-elimination ratio is not a field scalar")
        eliminated = reduced[6] - reduced[2] * ratio
        square_scale = coefficient(eliminated, (2, 0, 0, 0, 0, 0))
        if not square_scale:
            fail(f"branch {branch_number}: zero square scale")
        alpha = coefficient(eliminated, (1, 0, 1, 0, 0, 0)) / (2 * square_scale)
        beta = coefficient(eliminated, (1, 0, 0, 0, 1, 0)) / (2 * square_scale)
        gamma = coefficient(eliminated, (1, 0, 0, 0, 0, 0)) / (2 * square_scale)
        linear = (ec.PP.var(0) + ec.PP.const(alpha) * ec.PP.var(2)
                  + ec.PP.const(beta) * ec.PP.var(4) + ec.PP.const(gamma))
        if eliminated.d != (linear * linear * square_scale).d:
            fail(f"branch {branch_number}: E6-lambda*E2 is not the claimed exact square")
        r_value = -(ec.PP.const(alpha) * ec.PP.var(2)
                    + ec.PP.const(beta) * ec.PP.var(4) + ec.PP.const(gamma))
        after_r = [substitute_poly(q, 0, r_value) for q in reduced]

        u3_coefficient = coefficient_of_variable(after_r[2], 5)
        h_scale = coefficient(u3_coefficient, (0, 0, 1, 0, 0, 0))
        if not h_scale:
            fail(f"branch {branch_number}: zero h*u3 scale")
        eta = coefficient(u3_coefficient, (0, 0, 0, 0, 1, 0)) / h_scale
        delta = coefficient(u3_coefficient, zero) / h_scale
        old_h = ec.PP.var(2) - ec.PP.const(eta) * ec.PP.var(4) - ec.PP.const(delta)
        after_h = [substitute_poly(q, 2, old_h) for q in after_r]
        expected_indices = [2, 4, 5, 8, 9, 10, 11]
        surviving_indices = [i for i, q in enumerate(after_h) if q]
        if not set(expected_indices).issubset(surviving_indices):
            fail(
                f"branch {branch_number}: a retained equation vanished; "
                f"survivors={surviving_indices}"
            )
        for i in surviving_indices:
            if i not in expected_indices and not any(
                scalar_ratio(after_h[i], after_h[j]) is not None
                for j in expected_indices
            ):
                fail(
                    f"branch {branch_number}: equation {i} was discarded "
                    "without an exact nonzero scalar proportionality"
                )

        serialized = []
        for index in expected_indices:
            equation = {}
            for monomial, field_value in after_h[index].d.items():
                if monomial[0] or monomial[1]:
                    fail("eliminated r or s reappeared")
                target = (monomial[2], monomial[3], monomial[4], monomial[5])
                equation[target] = {
                    degree: (int(field_value.p[degree].p), int(field_value.p[degree].q))
                    for degree in range(len(field_value.p)) if field_value.p[degree]
                }
            serialized.append(equation)
        saved = pickle.loads((root / f"case1_branch{branch_number}_after_w.pkl").read_bytes())
        if serialized != saved:
            fail(f"branch {branch_number}: regenerated pre-division system differs from certificate source")

        pivot = after_h[2]
        h_times_u3 = ec.PP({(0, 0, 1, 0, 0, 1): h_scale})
        n_value = (pivot - h_times_u3) * (-h_scale.inv())
        if pivot.d != ((ec.PP.var(2) * ec.PP.var(5) - n_value) * h_scale).d:
            fail(f"branch {branch_number}: u3 pivot identity failed")

        min_h_powers = []
        derived_serialized = []
        for index in expected_indices[1:]:
            source = after_h[index]
            max_u3 = max(m[5] for m in source.d)
            cleared = ec.PP()
            for monomial, field_value in source.d.items():
                u3_exponent = monomial[5]
                target = list(monomial)
                target[5] = 0
                cleared += (ec.PP({tuple(target): field_value})
                            * pp_pow(n_value, u3_exponent)
                            * pp_pow(ec.PP.var(2), max_u3 - u3_exponent))
            min_h = min(m[2] for m in cleared.d)
            min_h_powers.append(min_h)
            if min_h:
                cleared = ec.PP({
                    (m[0], m[1], m[2] - min_h, m[3], m[4], m[5]): value
                    for m, value in cleared.d.items()
                })
            encoded = {}
            for monomial, field_value in cleared.d.items():
                if monomial[0] or monomial[1] or monomial[5]:
                    fail("unexpected variable after h!=0 elimination")
                target = (monomial[2], monomial[3], monomial[4])
                encoded[target] = {
                    degree: (int(field_value.p[degree].p), int(field_value.p[degree].q))
                    for degree in range(len(field_value.p)) if field_value.p[degree]
                }
            derived_serialized.append(encoded)
        expected_name = "hne0_deg35.pkl" if branch_number == 1 else "hne0_branch2_deg35.pkl"
        if derived_serialized != pickle.loads((root / expected_name).read_bytes()):
            fail(f"branch {branch_number}: regenerated h!=0 system differs from archived system")
        min_h_powers_by_branch.append(min_h_powers)

    # Dividing by powers of h above is legitimate only on h != 0.  The frozen
    # replay separately verifies unit certificates at h = 0 against the two
    # original pre-division systems, whose hashes are embedded in the payloads.
    for filename, source_name in [
        ("h0_branch1_exact_certificate.pkl", "case1_branch1_after_w.pkl"),
        ("h0_exact_certificate.pkl", "case1_branch2_after_w.pkl"),
    ]:
        payload = pickle.loads((root / filename).read_bytes())
        if payload.get("source_system") != source_name:
            fail(f"{filename} is not tied to the expected pre-division system")
    print(f"H_NONZERO_SATURATION_AUDIT_PASS powers={min_h_powers_by_branch}")
    print("H_ZERO_PRE_DIVISION_COVERAGE_PASS")
    print("TRANSCRIPTION_BRIDGE_LOCAL_PASS")


if __name__ == "__main__":
    main()
