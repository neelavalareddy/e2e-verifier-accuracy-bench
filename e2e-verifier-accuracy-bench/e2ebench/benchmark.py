"""Run the full benchmark and render reports (Markdown + JSON)."""
import json

from .dataset import SYNTHETIC_NOTICE, build_apps
from .judge import judge_app
from .metrics import compute_metrics
from .verifiers import VERIFIERS


def run_benchmark(apps=None, verifiers=None):
    apps = apps if apps is not None else build_apps()
    verifiers = verifiers if verifiers is not None else VERIFIERS
    out = {"synthetic_notice": SYNTHETIC_NOTICE, "apps": len(apps), "verifiers": {}}
    for name, fn in verifiers.items():
        js = [judge_app(a, fn(a)) for a in apps]
        out["verifiers"][name] = {"metrics": compute_metrics(js), "judgements": js}
    return out


def to_json(result, extra=None):
    d = dict(result)
    if extra:
        d.update(extra)
    return json.dumps(d, indent=2, sort_keys=True)


def _pct(x):
    return "%.1f%%" % (100 * x)


def to_markdown(result, banner=None):
    names = list(result["verifiers"])
    m = {n: result["verifiers"][n]["metrics"] for n in names}
    L = ["# Verifier-accuracy benchmark report", ""]
    if banner:
        L += [banner, ""]
    L += ["> " + result["synthetic_notice"], "",
          "| Metric | " + " | ".join(names) + " |",
          "|---|" + "---|" * len(names)]
    rows = [
        ("Defect detection rate (recall)", "defect_detection_rate"),
        ("False-pass rate (missed defects)", "false_pass_rate"),
        ("False-fail rate (clean apps flagged)", "false_fail_rate"),
        ("Traceability rate", "traceability_rate"),
    ]
    for label, key in rows:
        L.append("| %s | %s |" % (label, " | ".join(_pct(m[n][key]) for n in names)))
    L.append("| Defects detected | " + " | ".join(
        "%d/%d" % (m[n]["defects_detected"], m[n]["defects_total"]) for n in names) + " |")
    L.append("| Clean apps flagged | " + " | ".join(
        "%d/%d" % (m[n]["false_fail_apps"], m[n]["clean_apps"]) for n in names) + " |")
    L.append("| Check coverage | " + " | ".join(
        _pct(m[n]["check_level"]["coverage"]) for n in names) + " |")
    L += ["", "## Per-defect-class detection", "",
          "| Defect class | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    classes = sorted({c for n in names for c in m[n]["per_defect_class"]})
    for c in classes:
        cells = []
        for n in names:
            s = m[n]["per_defect_class"].get(c)
            cells.append("%d/%d" % (s["detected"], s["total"]) if s else "-")
        L.append("| %s | %s |" % (c, " | ".join(cells)))
    L += ["", "## Check-level confusion (checks the verifier ran)", "",
          "| Verifier | TP | FP | FN | TN | not run | accuracy |", "|---|---|---|---|---|---|---|"]
    for n in names:
        c = m[n]["check_level"]
        L.append("| %s | %d | %d | %d | %d | %d | %s |" % (
            n, c["tp"], c["fp"], c["fn"], c["tn"], c["not_run"],
            _pct(c["accuracy_on_run_checks"])))
    L += ["", "Note: the reference verifiers were written against this dataset, so "
          "scores validate the harness, not any real verifier.", ""]
    return "\n".join(L)

