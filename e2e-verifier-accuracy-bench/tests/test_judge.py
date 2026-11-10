import copy
import unittest

from e2ebench.dataset import build_apps
from e2ebench.judge import judge_app
from e2ebench.verifiers import verify_careful, verify_sloppy


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.apps = {a["id"]: a for a in build_apps()}

    def kinds(self, j):
        return {c["check_id"]: c["kind"] for c in j["checks"]}

    def test_layer1_tp_and_detection(self):
        a = self.apps["cartly"]
        j = judge_app(a, verify_careful(a))
        self.assertEqual(self.kinds(j)["cart_total:cart_table"], "tp")
        self.assertEqual(j["defects"], [{"class": "wrong_cart_total", "detected": True}])

    def test_layer1_not_run_and_miss(self):
        a = self.apps["cartly"]
        j = judge_app(a, verify_sloppy(a))
        self.assertEqual(self.kinds(j)["cart_total:cart_table"], "not_run")
        self.assertFalse(j["defects"][0]["detected"])
        self.assertEqual(j["app_verdict"], "pass")
        self.assertEqual(j["app_expected"], "fail")

    def test_layer1_fp(self):
        a = self.apps["launchpad"]
        j = judge_app(a, verify_sloppy(a))
        self.assertEqual(self.kinds(j)["main_button_present"], "fp")

    def test_layer1_fn(self):
        a = self.apps["cartly"]
        v = verify_careful(a)
        for c in v["checks"]:
            c["result"] = "pass"
        self.assertEqual(self.kinds(judge_app(a, v))["cart_total:cart_table"], "fn")

    def test_layer2_careful_fully_traceable(self):
        for a in self.apps.values():
            self.assertTrue(all(t["traceable"] for t in judge_app(a, verify_careful(a))["trace"]))

    def test_layer2_sloppy_loads_untraceable(self):
        a = self.apps["taskly"]
        t = {x["check_id"]: x for x in judge_app(a, verify_sloppy(a))["trace"]}
        self.assertFalse(t["loads"]["traceable"])
        self.assertTrue(t["no_console_error"]["traceable"])

    def test_layer2_failure_modes(self):
        a = self.apps["taskly"]
        v = copy.deepcopy(verify_careful(a))
        v["checks"][0]["cites"]["element"] = "ghost"
        v["checks"][1]["cites"]["check"] = "other"
        v["checks"][2]["evidence"] = "  "
        t = judge_app(a, v)["trace"]
        self.assertEqual([x["traceable"] for x in t[:4]], [False, False, False, True])


if __name__ == "__main__":
    unittest.main()

