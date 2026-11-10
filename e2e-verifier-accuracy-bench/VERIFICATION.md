# Execution verification

Verified on 2026-11-10 using installed CPython 3.13.13. All 15 source artifacts were retrieved using Mercury list_artifacts/read_artifact from task d5cdc584-765a-4725-a7fc-adaf321e53fe.

Executed from the package directory:
```
python -m unittest discover -s tests -t .
python demo.py --out out
```
The default shell had no python command; /usr/bin/python3 was an unusable Xcode stub. A temporary local PATH alias selected the already installed CPython runtime. No runtime installation was needed.

Tests: 32 run, 32 passed, zero failures/errors. See verification-evidence/tests.txt and demo.txt for actual captured output.

| Metric | careful | sloppy |
|---|---|---|
| Defects detected / recall | 8/8, 100% | 1/8, 12.5% |
| False-pass | 0% | 87.5% |
| False-fail | 0/4, 0% | 1/4, 25% |
| Traceability | 59/59, 100% | 24/36, 66.7% |
| Coverage | 59/59, 100% | 36/59, 61.0% |

All supplied claims match execution. Raw stored rates use four decimal places (sloppy traceability 0.6667, coverage 0.6102). Check confusion: careful TP=9 FP=0 FN=0 TN=50 not_run=0; sloppy TP=1 FP=1 FN=0 TN=34 not_run=23.

Code bug fixes: none. Thresholds, labels, ground truth and source/tests are unchanged. README honesty-note text was updated to identify measured synthetic results and the verified sample reports. sample_report/report.md and report.json were regenerated from the actual out/report.json using the package renderers, adding explicit generation provenance; no hand-derived banner remains. The regeneration and metric-comparison script is verification-evidence/finalize.py.

Independent Mercury static-audit delegation was attempted but rejected: “MCP tool call requires approval, but approval policy is never.” No delegated work is pending. Verification here rests on local execution and comparison.
