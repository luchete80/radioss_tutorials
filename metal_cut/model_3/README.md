# Model 3

This directory contains the two starter/engine input files and the material include from `model_2`. The two model input files are byte-identical copies of their `model_2` counterparts. No simulation outputs are included.

## Units and material

The source material values were supplied in the common kg, mm, ms unit system: density `2.8e-6 kg/mm^3`, Young's modulus `72,000 MPa`, and Johnson–Cook strengths `a = 250 MPa` and `b = 120 MPa`. The model deck uses kg, m, s, so the values in `material.rad` are converted to `rho = 2,800 kg/m^3`, `E = 72 GPa`, `a = 250 MPa`, and `b = 120 MPa`. Dimensionless values are `nu = 0.33`, `n = 0.18`, and `EPS_p_max = 1`; `SIG_max = 0`. The remaining requested Johnson–Cook rate, hardening, melt, and heat-capacity terms are zero.

Unit conversion follows Altair's Radioss unit consistency guidance: [unit consistency](https://2024.help.altair.com/2024.1/hwsolvers/rad/topics/solvers/rad/unit_consistency_debug_r.htm).

Material 2's `/FAIL/JOHNSON` card is replaced by `/FAIL/BIQUAD` with `c1=c2=c4=c5=0`, `c3=0.055`, `P_thick_fail=0`, `M_Flag=2`, `S_Flag=2`, and the remaining fields zero. The existing `/HEAT/MAT/2` card is retained unchanged, as are material 1, `/HEAT/MAT/1`, `/SURF/PART/EXT/2`, and `/FUNCT/1`.

BIQUAD card fields follow [Altair's `/FAIL/BIQUAD` reference](https://help.altair.com/hwsolvers/rad/topics/solvers/rad/fail_biquad_starter_r.htm).

## Validation

The parent audited the conversion and exact copies of the starter and engine inputs. OpenRadioss Starter accepted the final inputs with 0 errors and no BIQUAD syntax warnings. The failure card includes the trailing Fail_ID=0 required by the 2019 input format. Existing model warnings remain (property card, initial penetrations, overlapping kinematic conditions), plus a specific-heat mismatch: the retained HEAT/MAT/2 value takes precedence over the supplied zero rhoC_p. No full simulation was run. Validation output: /tmp/metal_cut_model3_final_btcdj40i.
