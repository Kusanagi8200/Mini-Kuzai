"""V70 unit tests: exact V69 replay, numerical metrics and no writes."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
SOURCE=ROOT/"tools"/"public-audits"/"phase03_v70_precision_control_001.py"
spec=importlib.util.spec_from_file_location("phase03_v70_controls",SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V70 test module unavailable")
V=importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def scenario():
    def item(ce,n,top,merge1,merge5,eos):
        return dict(zip(V.FIELDS,(ce,n,top,merge1,merge5,eos)))
    data={
        "BF16":item(4733,4,7258,326,685,14),
        "FP32":item(4734,4,7258,326,685,14),
        "HALF":item(4892,4,7098,331,727,23),
        "FULL":item(5048,7,6957,335,771,24),
    }
    m={}
    for mode,src in (("BF16","BASE"),("HALF","HALF"),("FULL","FULL")):
        for field,value in data[mode].items():
            if src=="BASE" and field=="EOS_TOP1":
                continue
            m[f"V69_NORM_{src}_{field}"]=value
    return data,m


class V70PrecisionControlTests(unittest.TestCase):
    def test_exactly_30_bounded_integer_metrics(self):
        data,_=scenario()
        output=V.build_report(data)
        self.assertEqual(len(output),30)
        self.assertEqual(output["V70_CTRL_PASS"],1)
        self.assertEqual(output["TRAINING_STARTED"],0)
        self.assertEqual(output["V70_CTRL_BLIND_ACCESS"],0)
        self.assertEqual(output["V70_CTRL_FULL_CE_X1000"],5048)
        self.assertTrue(all(type(n) is int for n in output.values()))

    def test_v69_reproduction_is_strict(self):
        data,prior=scenario()
        V.verify_reproduction(data,prior)
        data["FULL"]["CE_X1000"]+=1
        with self.assertRaises(RuntimeError):
            V.verify_reproduction(data,prior)

    def test_bf16_baseline_is_fixed(self):
        data,prior=scenario()
        data["BF16"]["EOS_TOP1"]=13
        with self.assertRaises(RuntimeError):
            V.verify_reproduction(data,prior)

    def test_fp32_control_does_not_need_identical_logits(self):
        data,prior=scenario()
        data["FP32"]["CE_X1000"]=4766
        data["FP32"]["PRED_DISTINCT"]=5
        V.verify_reproduction(data,prior)

    def test_reject_missing_mode(self):
        data,_=scenario()
        del data["FULL"]
        with self.assertRaises(RuntimeError):
            V.build_report(data)

    def test_reject_negative_or_noninteger_metrics(self):
        data,_=scenario()
        data["FP32"]["CE_X1000"]=-5
        with self.assertRaises(RuntimeError):
            V.build_report(data)
        data,_=scenario()
        data["FP32"]["CE_X1000"]=4.733
        with self.assertRaises(RuntimeError):
            V.build_report(data)

    def test_report_keys_stable(self):
        data,_=scenario()
        fields=V.build_report(data)
        self.assertEqual({k for k in fields if k.startswith("V70_CTRL_")},
                         {"V70_CTRL_PASS","V70_CTRL_BLIND_ACCESS",
                          "V70_CTRL_VAL_LEXICAL"} |
                         {f"V70_CTRL_{mode}_{field}" for mode in V.MODES for field in V.FIELDS})

    def test_readonly_audit_no_training_or_blind(self):
        c=SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("optimizer.step(",c)
        self.assertNotIn("torch.save(",c)
        self.assertNotIn("build_blind",c)
        self.assertNotIn("load_blind",c)
        self.assertIn("handle.remove()",c)
        self.assertIn("torch.equal(weights, before)",c)


if __name__=="__main__":
    unittest.main()
