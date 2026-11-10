import unittest

from e2ebench.dataset import (DEFECT_CLASSES, SYNTHETIC_NOTICE, build_apps,
                              check_ids, ground_truth, known_elements)


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.apps = build_apps()

    def test_counts(self):
        self.assertEqual(len(self.apps), 12)
        self.assertEqual(sum(1 for a in self.apps if a["defects"]), 8)
        self.assertEqual(sum(1 for a in self.apps if not a["defects"]), 4)

    def test_all_marked_synthetic(self):
        self.assertTrue(all(a["synthetic"] for a in self.apps))
        self.assertIn("SYNTHETIC", SYNTHETIC_NOTICE)

    def test_each_defect_class_once(self):
        classes = sorted(d["class"] for a in self.apps for d in a["defects"])
        self.assertEqual(classes, sorted(DEFECT_CLASSES))

    def test_unique_ids_and_defect_checks_exist(self):
        self.assertEqual(len({a["id"] for a in self.apps}), 12)
        for a in self.apps:
            ids = check_ids(a)
            self.assertEqual(len(ids), len(set(ids)))
            for d in a["defects"]:
                for c in d["checks"]:
                    self.assertIn(c, ids)
            for c in a["checks"]:
                self.assertIn(c["element"], known_elements(a))

    def test_ground_truth(self):
        by = {a["id"]: ground_truth(a) for a in self.apps}
        self.assertEqual(by["bookit"]["checks"]["no_console_error"], "fail")
        self.assertEqual(by["bookit"]["checks"]["handler_wired:submit_booking"], "fail")
        self.assertEqual(by["taskly"]["app_expected"], "pass")
        self.assertEqual(by["cartly"]["app_expected"], "fail")
        self.assertEqual(sum(v == "fail" for g in by.values() for v in g["checks"].values()), 9)
        self.assertEqual(sum(len(g["checks"]) for g in by.values()), 59)


if __name__ == "__main__":
    unittest.main()

