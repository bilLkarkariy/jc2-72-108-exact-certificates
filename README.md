# Exact certificates for the JC2 degree pair (72,108)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21479814.svg)](https://doi.org/10.5281/zenodo.21479814)
[![Exact clean-room replay](https://github.com/bilLkarkariy/jc2-72-108-exact-certificates/actions/workflows/exact-replay.yml/badge.svg)](https://github.com/bilLkarkariy/jc2-72-108-exact-certificates/actions/workflows/exact-replay.yml)

This repository accompanies the manuscript **Exact Certificates for the
(72,108) Frontier in the Two-Dimensional Jacobian Problem**.

The `v1.0.1` tag and DOI deposit are frozen. The current `v1.1` audit work is
developed separately and must not be described as a new archival release until
the clean-room workflow and external transcription review are complete.

## Status and scope

The archived computations replay exact characteristic-zero polynomial
identities for the two Laurent/Newton coefficient systems transcribed from
Proposition 4.3 of Guccione, Guccione, Horruitiner and Valqui,
[arXiv:2204.14178](https://arxiv.org/abs/2204.14178).

The exact replay ends with:

```text
ALL_SERIALIZED_EXACT_CERTIFICATES_PASS
GMPY2_EXACT_PASS
SYSTEM_SYMMETRY_PASS
BRANCH1_EXACT_IDENTITY_PASS
BRANCH2_EXACT_IDENTITY_PASS
JC2_72_108_EXACT_REPLAY_PASS
```

The computation excludes both **transcribed** coefficient systems. The
conclusion that the degree pair `(72,108)` is impossible, and hence that every
hypothetical plane counterexample has maximum degree at least 125, remains
conditional on the correctness and exhaustiveness of the published reduction
and on its faithful transcription. This is **not** a proof of the full
two-dimensional Jacobian conjecture. Independent mathematical and
computational review is requested.

## Contents

- `paper/`: English LaTeX manuscript and compiled PDF.
- `TRANSCRIPTION_AUDIT.md`: page-to-file audit of the interface from GGHV
  Proposition 4.3 to the certified coefficient systems.
- `CLAIMS_TO_FILES.md`: claim/equation/certificate/verifier matrix.
- `REPRODUCE.md`: clean-room Docker and direct-replay instructions.
- `scripts/verify_transcription_bridge.py`: exact checks for support coverage,
  normalization, exhaustive branching and component preservation.
- `tests/negative_controls.py`: five deliberate corruptions that every correct
  verifier must reject.
- `verification/RECONSTRUCTED_CERTIFICATES.sha256`: hashes of the reconstructed
  exact certificates and core replay scripts.
- `verification/verify_all_final.out`: saved successful replay output.
- `social/`: proposed public summary.
- `release_bundle/`: the complete exact replay workspace included directly in
  the archival source snapshot used by Zenodo.
- GitHub Release assets: the same complete replay workspace and a smaller
  selected-certificate archive.

## Exact certificate architecture

- Case 2 is excluded by an exact unit-ideal identity
  `1 = sum(T_i R_i)`.
- Case 1 splits exhaustively into `s = c` and `s = -c`.
- In the first branch, an exact identity `h = sum(T_i E_i)` forces `h = 0`.
- Exact unit-ideal certificates exclude the `h = 0` specialization in both
  branches.
- A checked algebraic involution transports the hard identity between the two
  sign branches.

The hard certificate is 89,105,967 bytes. Its multiplier ansatz expands to a
2010-by-1925 rational linear system. A fixed 1925-by-1925 minor has determinant
10 modulo 71. The recovered exact solution is verified against all 2010 scalar
equations. An independent `gmpy2` verifier evaluates 13,410 number-field
products, equivalent to 335,250 scalar products.

## Clean-room reproduction

The preferred path downloads the frozen archive from Zenodo only:

```bash
docker build --pull -t jc2-exact-audit .
docker run --rm jc2-exact-audit
```

The expected final marker is:

```text
JC2_72_108_CLEAN_ROOM_PASS
```

The image pins CPython 3.14.6 by manifest digest and installs only hashed,
version-locked Linux wheels. See [`REPRODUCE.md`](REPRODUCE.md).

## Direct frozen replay

Download and extract `jc2_72_108_exact_replay_v1.0.1.zip` from the latest
Release, then run:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
PYTHON="$PWD/.venv/bin/python" ./exact_replay/verify_all.sh
```

The expected final marker is:

```text
JC2_72_108_EXACT_REPLAY_PASS
```

The reference replay used Python 3.14 and completed in approximately 70
seconds on an Apple Silicon laptop. Runtime may vary substantially.

## Audit status

The local bridge checker and all five negative controls pass. A public Linux
x86-64 GitHub Actions run and external mathematical review remain required
before preparing a `v1.1.0` release. The four GGHV authors are being asked the
specific question: “Could you verify whether our transcription and use of
Proposition 4.3 are exhaustive?”

## Citation

Use the metadata in [`CITATION.cff`](CITATION.cff). The archival release is
available at [doi:10.5281/zenodo.21479814](https://doi.org/10.5281/zenodo.21479814).

## Licenses

The manuscript and documentation are released under CC BY 4.0. Verification
and reconstruction code is released under the MIT License. See
[`LICENSES.md`](LICENSES.md).

## AI assistance disclosure

OpenAI Codex assisted with certificate reconstruction, verification scripting,
and manuscript preparation. All central claims are tied either to exact
machine-checkable identities or to explicitly identified published inputs.
