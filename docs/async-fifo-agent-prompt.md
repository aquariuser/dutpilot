# Async FIFO Agent Prompt

Use this prompt to demonstrate explicit DUTPilot skill usage for a non-trivial RTL task.

```text
$dutpilot

Implement an asynchronous FIFO in Verilog and verify it with DUTPilot.

Requirements:
1. Before writing the testbench, follow the DUTPilot self-checking testbench contract.
2. Implement async_fifo.v.
3. Implement tb_async_fifo.v.
4. The testbench must use independent write/read clocks.
5. The testbench must include a scoreboard or reference queue.
6. The testbench must check read data order.
7. The testbench must check reset, empty, and full behavior at a basic level.
8. On mismatch, print DUTPILOT_FAIL: <reason>.
9. On success, print DUTPILOT_PASS.
10. Create dutpilot.yaml.
11. Run python3 -m dutpilot.cli verify <dutpilot.yaml>.
12. Read report.json.
13. If failed, fix RTL or testbench and rerun until status=passed.
```

For current DUTPilot v0.1 reports, `status=pass` is the passing value. The prompt uses `status=passed` as user-facing intent; the agent should interpret either form according to the active report schema.
