import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("converter", Path(__file__).with_name("convert.py"))
converter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(converter)


class ConverterTest(unittest.TestCase):
    def test_normalization_and_value_policy(self):
        rows = [
            (1, "负值", "nǜ zhi", "", "负值\tnǜ zhi\t1"),
            (2, "零值", "ling zhi", "", "零值\tling zhi\t1"),
            (3, "正值", "zhèng zhi", "", "正值\tzhèng zhi\t1"),
            (4, "新增", "xin zeng", "", "新增\txin zeng\t1"),
        ]
        official = {("负值", "nv'zhi"): -1.25, ("零值", "ling'zhi"): 0.0, ("正值", "zheng'zhi"): 2.0}
        entries, rejects, duplicates = converter.convert(rows, official)
        self.assertEqual(rejects, [])
        self.assertEqual(duplicates, 0)
        self.assertEqual(entries[("负值", "nv'zhi")], -1.25)
        self.assertEqual(entries[("零值", "ling'zhi")], 0.0)
        self.assertEqual(entries[("正值", "zheng'zhi")], 0.0)
        self.assertEqual(entries[("新增", "xin'zeng")], 0.0)

    def test_rejects_and_deduplicates(self):
        rows = [
            (1, "好", "hao", "", "好\thao"),
            (2, "好", "hao", "", "好\thao"),
            (3, "坏", "bad code!", "", "坏\tbad code!"),
            (4, "坏", "", "FIELDS", "坏"),
        ]
        entries, rejects, duplicates = converter.convert(rows, {})
        self.assertEqual(len(entries), 1)
        self.assertEqual(duplicates, 1)
        self.assertEqual([(r[0], r[1]) for r in rejects], [(3, "PINYIN"), (4, "FIELDS")])

    def test_pinyin_syllable_nan_is_not_a_numeric_weight(self):
        self.assertFalse(converter.numeric("nan"))
        self.assertFalse(converter.numeric("inf"))

    def test_output_is_sorted_and_stable(self):
        entries = {("乙", "yi"): 0.0, ("甲", "jia"): -1.0}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "out.txt"
            converter.write_text(path, entries)
            first = path.read_bytes()
            converter.write_text(path, entries)
            self.assertEqual(first, path.read_bytes())
            self.assertEqual(path.read_text(), "乙 yi 0\n甲 jia -1\n")

    def test_rime_imports_are_followed_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "top.dict.yaml").write_text(
                "name: top\nimport_tables:\n- child\n...\n", encoding="utf-8"
            )
            (root / "child.dict.yaml").write_text(
                "name: child\n---\n...\n子\tzi\n", encoding="utf-8"
            )
            rows = list(converter.parse_rime_tree(root, Path("top.dict.yaml")))
            entries, rejects, _ = converter.convert(rows, {})
            self.assertEqual(entries, {("子", "zi"): 0.0})
            self.assertEqual(rejects, [])

    def test_charmap_uses_highest_weight_single_character_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "8105.dict.yaml"
            path.write_text("---\n重\tzhong\t1\n重\tchong\t2\n", encoding="utf-8")
            self.assertEqual(converter.read_charmap(path), {"重": "chong"})

    def test_missing_rime_code_can_use_character_annotation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.dict.yaml"
            path.write_text("---\n...\n两个火\n", encoding="utf-8")
            rows = list(converter.parse_rime(path, {"两": "liang", "个": "ge", "火": "huo"}))
            entries, rejects, _ = converter.convert(rows, {})
            self.assertEqual(entries, {("两个火", "liang'ge'huo"): 0.0})
            self.assertEqual(rejects, [])


if __name__ == "__main__":
    unittest.main()
