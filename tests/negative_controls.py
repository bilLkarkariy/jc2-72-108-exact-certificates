#!/usr/bin/env python3
"""Deliberately corrupt frozen inputs and require the exact verifiers to fail."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import pickle
import subprocess
import sys
import tempfile
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def mutate_coefficient(container):
    """Add one to the first serialized rational coefficient found in-place."""
    if isinstance(container, list):
        for item in container:
            if mutate_coefficient(item):
                return True
    elif isinstance(container, dict):
        for key, value in container.items():
            if (isinstance(value, tuple) and len(value) == 2
                    and all(isinstance(x, int) for x in value)):
                numerator, denominator = value
                container[key] = (numerator + denominator, denominator)
                return True
            if mutate_coefficient(value):
                return True
    return False


def mutate_h0_equation(system):
    for equation in system:
        for monomial, coefficient in equation.items():
            if monomial[0] != 0:
                continue
            for degree, value in coefficient.items():
                numerator, denominator = value
                coefficient[degree] = (numerator + denominator, denominator)
                return True
    return False


def expect_failure(label, source):
    completed = subprocess.run(
        [sys.executable, "-c", source], text=True, capture_output=True
    )
    if completed.returncode == 0:
        raise RuntimeError(f"negative control unexpectedly passed: {label}")
    print(f"NEGATIVE_CONTROL_PASS {label}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: negative_controls.py EXACT_REPLAY_ROOT")
    root = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="jc2-negative-") as temp_name:
        temp = Path(temp_name)

        # 1. A byte-level change is rejected by the embedded source hash.
        source = root / "case1_branch1_after_w.pkl"
        corrupted_source = temp / source.name
        data = bytearray(source.read_bytes())
        data[-1] ^= 1
        corrupted_source.write_bytes(data)
        certificate = temp / "h0_branch1_exact_certificate.pkl"
        certificate.write_bytes((root / certificate.name).read_bytes())
        expect_failure("source_hash", f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(root)!r})
import verify_serialized_certificates as verifier
verifier.ROOT = Path({str(temp)!r})
verifier.verify_h0('h0_branch1_exact_certificate.pkl', 's=c')
""")

        # 2. A validly serialized multiplier coefficient is rejected by the
        # Case 2 exact identity, not merely by pickle parsing.
        case2_payload = pickle.loads((root / "case2_exact_certificate.pkl").read_bytes())
        if not mutate_coefficient(case2_payload["multipliers"]):
            raise RuntimeError("could not mutate a Case 2 multiplier")
        (temp / "case2_exact_certificate.pkl").write_bytes(pickle.dumps(case2_payload, protocol=4))
        expect_failure("certificate_coefficient", f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(root)!r})
import verify_serialized_certificates as verifier
verifier.ROOT = Path({str(temp)!r})
verifier.verify_case2()
""")

        # 3. Change an equation, update its hash to prevent the hash guard from
        # firing, and require generator regeneration itself to reject it.
        equation_system = pickle.loads(source.read_bytes())
        if not mutate_h0_equation(equation_system):
            raise RuntimeError("could not mutate a pre-division equation")
        changed_equation = pickle.dumps(equation_system, protocol=4)
        corrupted_source.write_bytes(changed_equation)
        h0_payload = pickle.loads((root / "h0_branch1_exact_certificate.pkl").read_bytes())
        h0_payload["source_sha256"] = hashlib.sha256(changed_equation).hexdigest()
        certificate.write_bytes(pickle.dumps(h0_payload, protocol=4))
        expect_failure("equation_regeneration", f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(root)!r})
import verify_serialized_certificates as verifier
verifier.ROOT = Path({str(temp)!r})
verifier.verify_h0('h0_branch1_exact_certificate.pkl', 's=c')
""")

        # 4. An altered branch equation must break the exact involution before
        # the expensive hard-certificate replay is reached.
        branch2 = pickle.loads((root / "hne0_branch2_polred.pkl").read_bytes())
        if not mutate_coefficient(branch2):
            raise RuntimeError("could not mutate a branch-symmetry coefficient")
        changed_branch = temp / "hne0_branch2_polred.pkl"
        changed_branch.write_bytes(pickle.dumps(branch2, protocol=4))
        expect_failure("branch_symmetry", f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(root)!r})
import verify_hne0_branch_symmetry as verifier
verifier.BRANCH2 = Path({str(changed_branch)!r})
verifier.main()
""")

        # 5. Change one exact rational solution coordinate in the 89 MB text
        # identity.  The independent gmpy2 scalar replay must reject it.
        original_h = root / "hard" / "h_certificate_exact.txt"
        changed_h = temp / "h_certificate_exact.txt"
        changed = False
        with original_h.open() as source_handle, changed_h.open("w") as target_handle:
            for line in source_handle:
                if not changed and line.startswith("C|"):
                    parts = line.rstrip("\n").split("|", 5)
                    expression = parts[5]
                    first, separator, rest = expression.partition("+")
                    if first.startswith("(") and ")" in first:
                        close = first.index(")")
                        rational = first[1:close]
                        if "/" in rational:
                            numerator, denominator = map(int, rational.split("/", 1))
                        else:
                            numerator, denominator = int(rational), 1
                        first = f"({numerator + denominator}/{denominator})" + first[close + 1:]
                        parts[5] = first + (separator + rest if separator else "")
                        line = "|".join(parts) + "\n"
                        changed = True
                target_handle.write(line)
        if not changed:
            raise RuntimeError("could not mutate the hard certificate")
        hard_verifier = root / "hard" / "verify_certificate_gmpy2.py"
        expect_failure("hard_rational_coordinate", f"""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('hard_negative', {str(hard_verifier)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.CERTIFICATE = Path({str(changed_h)!r})
module.main()
""")

    print("ALL_NEGATIVE_CONTROLS_PASS")


if __name__ == "__main__":
    main()
