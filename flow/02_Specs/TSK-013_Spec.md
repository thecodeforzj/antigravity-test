# TSK-013: AOS Formula Compiler Specification

## 1. Context

Automate the maping of high-level mathematical expressions to AOS 3.5 compliant DSL sequences. focus on FMA (Y=A\*C+B) vector compression at II=1.

## 2. Hard-Wire Compliance (Critical)

The compiler MUST honor the `ports_to_rtovr` defined in unit YAMLs:

- FPMUL: S0 -> rtovr_3, S1 -> rtovr_4, D -> Index 3
- FPADD: S0 -> rtovr_5, S1 -> rtovr_6, D -> Index 4
- RTOVR: 40 instances total.

## 3. Macro-Compression Logic

- Loop folding for II=1.
- DLY staggered routing (1-cycle for input, 5+ cycles for intermediate).
- Auto-INC support for vector operands.

## 4. Verification

- SMT solver must reach SAT for every generated DSL.
- Visual timing diagrams must show clean unit staggering.
