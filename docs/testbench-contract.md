# DUTPilot Testbench Contract

DUTPilot requires self-checking testbenches because the tool does not understand the intended function of an arbitrary RTL module. Functional correctness is judged by the checker logic inside the testbench.

DUTPilot's role is narrower:

- Stage the DUT and testbench into a run directory.
- Compile and run the simulator.
- Parse `DUTPILOT_PASS` and `DUTPILOT_FAIL` markers.
- Collect logs and waveform artifacts.
- Generate `report.json` and `summary.md`.

## Marker Semantics

`DUTPILOT_PASS` means all checks encoded in the provided testbench passed.

`DUTPILOT_FAIL: <reason>` means the testbench detected a mismatch or invalid condition. The reason should be specific enough for an agent or human to debug the failure.

A testbench that only applies stimulus and exits is not a DUTPilot validation testbench, even if the simulator exits with code 0.

## Required Behavior

A DUTPilot-compatible testbench must:

- Apply stimulus.
- Derive expected behavior from the spec, user request, interface semantics, or explicit assumptions.
- Compare DUT outputs against expected results.
- Print `DUTPILOT_FAIL: <reason>` on mismatch.
- Terminate after a failure with `$fatal`, `$error` followed by termination, or `$finish`.
- Print `DUTPILOT_PASS` only after all checks pass.
- Call `$finish`.
- Preferably generate `waves/wave.vcd`.

Recommended VCD setup:

```verilog
$dumpfile("waves/wave.vcd");
$dumpvars(0, <tb_top>);
```

## Bad Example

This testbench only provides stimulus. It does not check outputs and should not be treated as DUTPilot validation.

```verilog
initial begin
    a = 1;
    b = 2;
    #10;
    $finish;
end
```

## Good Example

This testbench compares observed output against an expected result and emits explicit markers.

```verilog
initial begin
    a = 1;
    b = 2;
    #1;
    if (sum !== 3) begin
        $display("DUTPILOT_FAIL: expected sum=3, got %0d", sum);
        $fatal;
    end
    $display("DUTPILOT_PASS");
    $finish;
end
```

## Complex Module Guidance

For a complex module such as an asynchronous FIFO, a useful DUTPilot testbench should include:

- Independent write and read clocks.
- Reset sequence.
- Write and read stimulus.
- Scoreboard or reference queue.
- Basic `empty` and `full` checks.
- Data order checks.
- `DUTPILOT_FAIL: <reason>` on any mismatch.
- `DUTPILOT_PASS` only after all checks pass.

If expected behavior is unclear, the agent should ask for missing requirements or explicitly state that it is only writing a minimal smoke test, not complete functional validation.
