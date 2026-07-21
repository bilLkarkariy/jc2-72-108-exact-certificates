# Claim-to-artifact map

This table identifies what is published input, what is locally regenerated,
and what an exact verifier actually proves.

| Claim | Equation/data source | Certificate or check | Independent verifier | Status |
|---|---|---|---|---|
| Only `(72,108)` and `(108,72)` remain below `125`. | GGHV Theorem 2.1, PDF p. 2 | None; published theorem | External mathematical review required | Published input |
| The `(8,28)` case yields exactly two polygon pairs with `[P,Q]=x^2`. | GGHV Proposition 4.3, PDF pp. 10--12 | Primary-source comparison in `TRANSCRIPTION_AUDIT.md` | Human line-by-line audit requested | Published input, locally transcribed |
| The polygon vertices give the implemented lattice bands. | Four vertex lists | Fresh lattice enumeration | `scripts/verify_transcription_bridge.py` | Locally exact |
| `t=xy^2,z=y^-1` gives `[t,z]=-1`, `x^2=t^2z^4`, and `(J4)`--`(J0)`. | Generic symbolic ansatz | Symbolic differentiation | Frozen `verify_laurent_reduction.py` and new bridge verifier | Locally exact |
| The vertex normalization is reversible and preserves `[P,Q]=x^2`. | Three nonzero `P` vertex coefficients | Symbolic scaling identities | `scripts/verify_transcription_bridge.py` | Locally exact; external conceptual review requested |
| The degree-35 first block represents all normalized `(J4)` solutions. | Frozen `exact_core.py`, `firstblock_Q_exact.out` | Triangular reconstruction and lex reduction | Frozen `verify_firstblock_exact.py` | Locally exact |
| Case 2 has no common zero. | Freshly regenerated Case 2 residuals | `case2_exact_certificate.pkl`: `1=sum(T_i R_i)` | Frozen `verify_serialized_certificates.py` | Exact characteristic zero |
| The Case 1 sign split is exhaustive. | First of 13 compatibility equations | `kappa(s^2-c^2)^2` checked directly | `scripts/verify_transcription_bridge.py` | Locally exact |
| `r` elimination loses no component. | Exact pair `E2,E6` | `E6-lambda E2=S L^2` | `scripts/verify_transcription_bridge.py` | Locally exact |
| The seven branch systems equal the regenerated pre-division equations. | `case1_checkpoint.pkl` | Byte-structural equality of serialized coefficients | `scripts/verify_transcription_bridge.py` | Locally exact |
| The `h!=0` equations follow from the pre-division systems. | `case1_branch*_after_w.pkl` | Termwise cleared `u3=N/h` substitution | `scripts/verify_transcription_bridge.py` | Locally exact |
| The `h=0` branch is not lost. | Original pre-division branch systems | `h0_branch1_exact_certificate.pkl`, `h0_exact_certificate.pkl` | Frozen `verify_serialized_certificates.py` checks source hashes and unit identities | Exact characteristic zero |
| The hard branch forces `h=0`. | `hne0_polred.pkl` | `hard/h_certificate_exact.txt`: `h=sum(T_i E_i)` | Frozen `hard/verify_certificate_gmpy2.py` | Exact characteristic zero |
| The second sign branch receives the hard identity. | `hne0_polred.pkl`, `hne0_branch2_polred.pkl` | Exact sign involution | Frozen `verify_hne0_branch_symmetry.py` | Exact characteristic zero |
| Verifiers reject corrupted data. | Deliberately changed certificate coefficient, equation, hash, symmetry coefficient and hard rational coordinate | Five negative controls | `tests/negative_controls.py` | Locally tested |
| A clean host can reproduce from Zenodo alone. | Frozen Zenodo snapshot and pinned Python environment | Local Zenodo-only run | `scripts/clean_room_replay.sh`, `verification/CLEAN_ROOM_LOCAL.out` | Passed on macOS arm64 |
| Linux x86-64 reproduces from Zenodo alone. | Frozen Zenodo snapshot and pinned Docker image/dependencies | Docker/GitHub Actions clean-room workflow | `.github/workflows/exact-replay.yml` | Pending first public CI run |

The exact certificates prove statements about the transcribed systems. The
degree-`125` corollary also depends on the published reduction and the faithful
interface audited in `TRANSCRIPTION_AUDIT.md`.
