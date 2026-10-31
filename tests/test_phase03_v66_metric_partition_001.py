"""V66 numeric-only GOGIT partition integrity; CPU-only, no checkpoint access."""
from __future__ import annotations

import unittest
from tools import phase03_v66_metric_partition as P


class V66MetricPartitionTests(unittest.TestCase):
    def report(self):
        P.check_partition()
        return {
            **{k:0 for k in P.SAFETY_KEYS},
            **{k:(1 if k=="V66_BIAS_PASS" else 0) for k in P.ALL_CUSTOM_KEYS},
        }

    def test_exact_partition_and_no_loss(self):
        P.check_partition()
        self.assertEqual(len(P.ALL_CUSTOM_KEYS),54)
        self.assertEqual(len(P.PART_A_KEYS),27)
        self.assertEqual(len(P.PART_B_KEYS),27)
        self.assertFalse(set(P.PART_A_KEYS)&set(P.PART_B_KEYS))
        self.assertEqual(set(P.PART_A_KEYS)|set(P.PART_B_KEYS),set(P.ALL_CUSTOM_KEYS))

    def test_each_publication_capped_at_30_metrics(self):
        original=self.report()
        a=P.select_part(original,"A")
        b=P.select_part(original,"B")
        self.assertEqual(len(a),30)
        self.assertEqual(len(b),30)
        self.assertEqual(set(a)&set(b),set(P.SAFETY_KEYS))
        merged={**a,**b}
        self.assertEqual(merged,original)

    def test_a_contains_confusion_mass_and_required_frozen_gates(self):
        a=P.select_part(self.report(),"A")
        for key in ("V66_BIAS_PASS","V66_BIAS_VAL_TOKENS","V66_BIAS_CONF_B_PB",
                    "V66_BIAS_CONF_M_PS","V66_BIAS_MASS_B_B_BP",
                    "V66_BIAS_MASS_M_M_BP","V66_BIAS_B0_COUNT"):
            self.assertIn(key,a)
        self.assertNotIn("V66_BIAS_M100_999_COUNT",a)

    def test_b_contains_all_non_b0_detailed_bins(self):
        b=P.select_part(self.report(),"B")
        for family in ("B","M"):
            for tier in ("1_9","10_99","100_999","1000P"):
                for metric in ("COUNT","TOP1_BP","NLL_X1000"):
                    self.assertIn(f"V66_BIAS_{family}{tier}_{metric}",b)
        for metric in ("COUNT","TOP1_BP","NLL_X1000"):
            self.assertIn(f"V66_BIAS_M0_{metric}",b)
        self.assertNotIn("V66_BIAS_PASS",b)
        self.assertNotIn("V66_BIAS_B0_COUNT",b)

    def test_fails_on_unknown_or_missing_metric(self):
        original=self.report()
        original.pop("V66_BIAS_M10_99_COUNT")
        with self.assertRaises(RuntimeError):
            P.select_part(original,"A")
        original=self.report()
        original["SECRET_VALUE"]=1234
        with self.assertRaises(RuntimeError):
            P.select_part(original,"B")

    def test_fails_on_unknown_part(self):
        with self.assertRaises(RuntimeError):
            P.select_part(self.report(),"C")

    def test_rejects_non_integer_metric(self):
        report=self.report()
        report["V66_BIAS_B10_99_COUNT"]="1337"
        with self.assertRaises(RuntimeError):
            P.select_part(report,"B")

    def test_safety_flag_fields_in_both_parts(self):
        original=self.report()
        for part in ("A","B"):
            result=P.select_part(original,part)
            for flag in P.SAFETY_KEYS:
                self.assertEqual(result[flag],0)
        self.assertEqual(P.select_part(original,"A")["V66_BIAS_PASS"],1)


if __name__=="__main__":
    unittest.main()
