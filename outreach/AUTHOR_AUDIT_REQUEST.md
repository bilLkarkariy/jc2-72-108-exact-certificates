Subject: Request for audit: exact certificates for Proposition 4.3, case (8,28)

Dear Professor [Surname],

I am an independent researcher working on the remaining `(72,108)` degree
configuration from your 2022 paper with Jorge A. Guccione, Juan J. Guccione,
Rodrigo Horruitiner and Christian Valqui.

I have reconstructed exact characteristic-zero certificates that exclude the
two coefficient systems obtained from Proposition 4.3, Case `(8,28)`. The
frozen replay package is archived here:

- Zenodo: https://doi.org/10.5281/zenodo.21479814
- GitHub: https://github.com/bilLkarkariy/jc2-72-108-exact-certificates

The package verifies explicit polynomial identities, including an 89.1 MB
identity over a degree-five number field. It ends with
`JC2_72_108_EXACT_REPLAY_PASS`. I am deliberately treating the degree-125
consequence as conditional, not established: the main remaining risk is the
interface between your published reduction and my coefficient systems.

Could you verify whether my transcription and use of Proposition 4.3 are
exhaustive? In particular, I would be grateful for a check of:

1. the two Newton polygons and `[P,Q]=x^2`;
2. the torus normalization of three nonzero vertex coefficients;
3. the complete coefficient supports after `t=xy^2`, `z=y^(-1)`;
4. the claim that no division, branch split or saturation removes a component.

The new audit document and machine checker are in the draft `v1.1` pull
request: [DRAFT PR URL].

This is not presented as a proof of JC(2). I would welcome a correction even
if the audit reveals a gap.

Kind regards,

Billel Helali

Independent Researcher, France
