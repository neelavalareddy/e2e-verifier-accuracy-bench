"""Metrics over a list of judge_app() outputs for one verifier."""


def _rate(n, d):
    return round(n / d, 4) if d else 0.0


def compute_metrics(judgements):
    defect_total = defect_hit = 0
    per_class = {}
    clean = defective = false_fail = 0
    tp = fp = fn = tn = not_run = 0
    tr_total = tr_ok = 0
    for j in judgements:
        if j["app_expected"] == "pass":
            clean += 1
            if j["app_verdict"] == "fail":
                false_fail += 1
        else:
            defective += 1
        for d in j["defects"]:
            defect_total += 1
            s = per_class.setdefault(d["class"], {"total": 0, "detected": 0})
            s["total"] += 1
            if d["detected"]:
                defect_hit += 1
                s["detected"] += 1
        for c in j["checks"]:
            k = c["kind"]
            tp += k == "tp"
            fp += k == "fp"
            fn += k == "fn"
            tn += k == "tn"
            not_run += k == "not_run"
        for t in j["trace"]:
            tr_total += 1
            tr_ok += bool(t["traceable"])
    run = tp + fp + fn + tn
    gt_checks = run + not_run
    for s in per_class.values():
        s["detection_rate"] = _rate(s["detected"], s["total"])
    return {
        "apps_total": len(judgements),
        "defective_apps": defective,
        "clean_apps": clean,
        "defects_total": defect_total,
        "defects_detected": defect_hit,
        "defect_detection_rate": _rate(defect_hit, defect_total),
        "false_pass_rate": _rate(defect_total - defect_hit, defect_total),
        "false_fail_apps": false_fail,
        "false_fail_rate": _rate(false_fail, clean),
        "per_defect_class": {k: per_class[k] for k in sorted(per_class)},
        "traceable_verdicts": tr_ok,
        "verdicts_total": tr_total,
        "traceability_rate": _rate(tr_ok, tr_total),
        "check_level": {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn, "not_run": not_run,
            "coverage": _rate(run, gt_checks),
            "accuracy_on_run_checks": _rate(tp + tn, run),
        },
    }

