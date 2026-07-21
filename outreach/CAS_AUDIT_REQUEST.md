Subject: Independent exact-arithmetic audit requested for a Jacobian certificate package

Dear [Name],

I am seeking an independent computer-algebra audit of an exact certificate
package for two Laurent-polynomial systems arising from the planar Jacobian
degree pair `(72,108)`.

Frozen artifacts: https://doi.org/10.5281/zenodo.21479814

Repository: https://github.com/bilLkarkariy/jc2-72-108-exact-certificates

The main checks are a Case 2 unit-ideal identity, two `h=0` unit identities,
and an 89.1 MB identity `h=sum(T_i E_i)` over a degree-five number field. The
supplied independent `gmpy2` verifier expands the last identity into 2010
rational scalar equations and reports 335,250 scalar products.

Would you be willing to replay the release on an independent machine and
review whether the verifiers trust any data they are intended to check? A
particularly valuable audit would reimplement the final identities in a
second CAS or a small independent exact-arithmetic program.

The claimed degree-125 consequence remains explicitly conditional on a
separate mathematical audit of the published reduction.

Kind regards,

Billel Helali

Independent Researcher, France
