import unittest

from e2ebench import dataset as D
from e2ebench import verifiers as V


def app(**kw):
    base = {"id": "x", "pages": ["/"], "elements": [], "loads": True,
            "console": [], "checks": [], "defects": []}
    base.update(kw)
    return base


class SurfaceTests(unittest.TestCase):
    def test_loads(self):
        self.assertEqual(V.check_loads(app())["result"], "pass")
        self.assertEqual(V.check_loads(app(loads=False))["result"], "fail")
        self.assertIsNone(V.check_loads(app(), cite_element=False)["cites"]["element"])

    def test_console_ignores_warnings(self):
        self.assertEqual(V.check_console(app(console=[{"level": "warn", "msg": "w"}]))["result"], "pass")
        r = V.check_console(app(console=[{"level": "error", "msg": "boom"}]))
        self.assertEqual(r["result"], "fail")
        self.assertIn("boom", r["evidence"])

    def test_main_button_kinds(self):
        a = app(elements=[{"id": "go", "kind": "link", "primary": True}])
        self.assertEqual(V.check_main_button(a)["result"], "pass")
        self.assertEqual(V.check_main_button(a, kinds=("button",))["result"], "fail")


class FeatureTests(unittest.TestCase):
    def test_handler(self):
        self.assertEqual(V.check_handler(None, D.handler("b"))["result"], "pass")
        self.assertEqual(V.check_handler(None, D.handler("b", False))["result"], "fail")

    def test_cart_total(self):
        self.assertEqual(V.recompute_total([[1999, 2], [500, 1]], 10), 4049)
        self.assertEqual(V.check_cart_total(None, D.total("t", [[1999, 2], [500, 1]], 10, 4049))["result"], "pass")
        self.assertEqual(V.check_cart_total(None, D.total("t", [[1999, 2], [500, 1]], 10, 2250))["result"], "fail")

    def test_auth(self):
        self.assertEqual(V.check_auth(None, D.auth("/d", "/login"))["result"], "pass")
        self.assertEqual(V.check_auth(None, D.auth("/d", "/d"))["result"], "fail")

    def test_pagination(self):
        self.assertEqual(V.check_pagination(None, D.pagination("l", 25, 10, 3))["result"], "pass")
        self.assertEqual(V.check_pagination(None, D.pagination("l", 40, 10, 4))["result"], "pass")
        self.assertEqual(V.check_pagination(None, D.pagination("l", 41, 10, 4))["result"], "fail")

    def test_save_refresh(self):
        self.assertEqual(V.simulate_save(D.save_refresh("e", "a", "b", True)), ("b", "b"))
        self.assertEqual(V.check_save_refresh(None, D.save_refresh("e", "a", "b", False))["result"], "fail")

    def test_mobile_nav(self):
        self.assertEqual(V.check_mobile_nav(None, D.mobile_nav("n", True))["result"], "pass")
        self.assertEqual(V.check_mobile_nav(None, D.mobile_nav("n", False))["result"], "fail")

    def test_double_click(self):
        self.assertEqual(V.simulate_double_click(D.double_click("p", True)), 1)
        self.assertEqual(V.check_double_click(None, D.double_click("p", False))["result"], "fail")

    def test_tz(self):
        self.assertEqual(V.check_tz(None, D.tz("t", "2026-03-01T02:30:00", -5, -5))["result"], "pass")
        r = V.check_tz(None, D.tz("t", "2026-03-01T02:30:00", -5, 5))
        self.assertEqual(r["result"], "fail")
        self.assertIn("2026-02-28", r["evidence"])


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.apps = {a["id"]: a for a in D.build_apps()}

    def test_careful_matches_ground_truth_everywhere(self):
        for a in self.apps.values():
            v = V.verify_careful(a)
            gt = D.ground_truth(a)
            self.assertEqual({c["check_id"]: c["result"] for c in v["checks"]}, gt["checks"])
            self.assertEqual(v["verdict"], gt["app_expected"])

    def test_sloppy_runs_only_surface(self):
        for a in self.apps.values():
            ids = [c["check_id"] for c in V.verify_sloppy(a)["checks"]]
            self.assertEqual(ids, list(D.SURFACE_CHECKS))

    def test_sloppy_known_behaviour(self):
        self.assertEqual(V.verify_sloppy(self.apps["bookit"])["verdict"], "fail")
        self.assertEqual(V.verify_sloppy(self.apps["cartly"])["verdict"], "pass")
        self.assertEqual(V.verify_sloppy(self.apps["launchpad"])["verdict"], "fail")


if __name__ == "__main__":
    unittest.main()

