---
type: "Project-Plan"
aos_stage: "P2"
status: "Active"
---

# SMT Compiler Scheduling Algorithm Implementation Plan

## 1. Requirement Refinement (P2 Specs)
### 1.1 Decision on Instruction Form
We represent an instruction stream as a list of operations:
- `FIXED_ADD(dst, src0, src1)`: Uses `fpadd`.
- `FIXED_MUL(dst, src0, src1)`: Uses `fpmul`.
- `BANK_READ(dst, bank_id, addr)`: Uses `ur_read`.
- `BANK_WRITE(src, bank_id, addr)`: Uses `ur_write`.

### 1.2 Constraint Mapping
1.  **Issue Constraint**: Only one unit of `fpadd` and `fpmul` available. Up to 4 `ur_read` and 4 `ur_write` per cycle.
2.  **Latency Constraint**: 
    - `fpadd`/`fpmul`: result available at `issue_cycle + 4`.
    - `ur_read`/`ur_write`/`rtovr`: result available at `issue_cycle + 1`.
3.  **Bank Conflict**: For any cycle `T`, the set of `bank_id` accessed by `ur_read` and `ur_write` must be disjoint.
4.  **Data Dependency**: `issue_cycle(instr_B) >= available_cycle(res_A)` if B depends on A.

## 2. Technical Stack (P3 Develop)
- **Language**: Python 3.10+
- **Library**: `z3-solver`
- **Output**: JSON trace + Gantt-style execution chart.

## 3. Success Criteria (AC)
- All instructions scheduled in minimal total cycles.
- No two `ur` operations access the same bank in the same cycle.
- All latencies respected (no RAW hazards).
- Structural hazards avoided.

## 4. Next Steps
1.  Verify the input format for the instruction stream.
2.  Implement the Python wrapper for Z3.
3.  Test with a trivial sequence (Read -> Add -> Mul -> Write).
