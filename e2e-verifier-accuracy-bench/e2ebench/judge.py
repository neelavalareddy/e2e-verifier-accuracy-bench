"""Two-layer judge.

Layer 1 (deterministic): verifier verdict vs ground truth, per check.
Layer 2 (traceability): each reported check must cite a known element and its
own check id, and carry non-empty evidence.
"""
from .dataset import ground_truth, known_elements


def judge_layer1(app, verdict):
    gt = ground_truth(app)
    by_id = {c["check_id"]: c["result"] for c in verdict["checks"]}
    rows = []
    for cid, exp in gt["checks"].items():
        act = by_id.get(cid, "not_run")
        if act == "not_run":
            kind = "not_run"
        elif exp == "fail":
            kind = "tp" if act == "fail" else "fn"
        else:
            kind = "fp" if act == "fail" else "tn"
        rows.append({"check_id": cid, "expected": exp, "actual": act, "kind": kind})
    defects = []
    for d in gt["defects"]:
        hit = any(by_id.get(c) == "fail" for c in d["checks"])
        defects.append({"class": d["class"], "detected": hit})
    return {"app_expected": gt["app_expected"], "app_verdict": verdict["verdict"],
            "checks": rows, "defects": defects}


def judge_layer2(app, verdict):
    known = known_elements(app)
    valid_ids = set(ground_truth(app)["checks"])
    rows = []
    for c in verdict["checks"]:
        cites = c.get("cites") or {}
        reason = None
        if cites.get("element") not in known:
            reason = "missing or unknown element"
        elif cites.get("check") != c["check_id"] or c["check_id"] not in valid_ids:
            reason = "missing or mismatched check citation"
        elif not str(c.get("evidence", "")).strip():
            reason = "empty evidence"
        rows.append({"check_id": c["check_id"], "traceable": reason is None,
                     "reason": reason})
    return rows


def judge_app(app, verdict):
    j = judge_layer1(app, verdict)
    j["app_id"] = app["id"]
    j["verifier"] = verdict["verifier"]
    j["trace"] = judge_layer2(app, verdict)
    return j

