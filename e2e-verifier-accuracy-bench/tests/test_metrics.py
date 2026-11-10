import json
import unittest

from e2ebench.benchmark import run_benchmark, to_json, to_markdown
from e2ebench.metrics import compute_metrics


def j(expected, verdict, defects=(), kinds=(), trace=()):
    return {"app_expected": expected, "app_verdict": verdict,
            "defects": [{"class": c, "detected": d} for c, d in defects],
            "checks": [{"kind": k} for k in kinds],
            "trace": [{"traceable": t} for t in trace]}


class MetricsUnitTests(unittest.TestCase):
    def test_hand_built(self):
        m = compute_metrics([
            j("fail", "fail", [("a", True)], ["tp", "tn"], [True, True]),
            j("fail", "pass", [("a", False), ("b", False)], ["fn", "not_run"], [True, False]),
            j("pass", "fail", [], ["fp"], [False]),
            j("pass", "pass", [], ["tn"], [True]),
        ])
        self.assertEqual(m["defects_total"], 3)
        self.assertEqual(m["defect_detection_rate"], 0.3333)
        self.assertEqual(m["false_pass_rate"], 0.6667)
        self.assertEqual(m["false_fail_rate"], 0.5)
        self.assertEqual(m["per_defect_class"]["a"], {"total": 2, "detected": 1, "detection_rate": 0.5})
        self.assertEqual(m["per_defect_class"]["b"]["detected"], 0)
        self.assertEqual(m["traceability_rate"], 0.6667)
        cl = m["check_level"]
        self.assertEqual((cl["tp"], cl["fp"], cl["fn"], cl["tn"], cl["not_run"]), (1, 1, 1, 2, 1))
        self.assertEqual(cl["coverage"], 0.8333)
        self.assertEqual(cl["accuracy_on_run_checks"], 0.6)

    def test_empty(self):
        m = compute_metrics([])
        self.assertEqual(m["defect_detection_rate"], 0.0)
        self.assertEqual(m["traceability_rate"], 0.0)


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.r = run_benchmark()
        self.m = {k: v["metrics"] for k, v in self.r["verifiers"].items()}

    def test_careful(self):
        c = self.m["careful"]
        self.assertEqual((c["defects_detected"], c["defects_total"]), (8, 8))
        self.assertEqual(c["false_pass_rate"], 0.0)
        self.assertEqual(c["false_fail_apps"], 0)
        self.assertEqual(c["traceability_rate"], 1.0)
        self.assertEqual(c["check_level"]["tp"], 9)
        self.assertEqual(c["check_level"]["tn"], 50)

    def test_sloppy(self):
        s = self.m["sloppy"]
        self.assertEqual(s["defects_detected"], 1)
        self.assertEqual(s["defect_detection_rate"], 0.125)
        self.assertEqual(s["false_pass_rate"], 0.875)
        self.assertEqual(s["false_fail_rate"], 0.25)
        self.assertEqual((s["traceable_verdicts"], s["verdicts_total"]), (24, 36))
        self.assertEqual(s["traceability_rate"], 0.6667)
        self.assertEqual(s["per_defect_class"]["broken_submit_handler"]["detected"], 1)
        self.assertEqual(s["check_level"]["not_run"], 23)

    def test_deterministic(self):
        self.assertEqual(to_json(self.r), to_json(run_benchmark()))

    def test_reports(self):
        md = to_markdown(self.r)
        self.assertIn("SYNTHETIC", md)
        self.assertIn("careful", md)
        self.assertEqual(json.loads(to_json(self.r))["apps"], 12)


if __name__ == "__main__":
    unittest.main()

