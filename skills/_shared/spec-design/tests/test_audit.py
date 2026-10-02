"""Black-box tests for audit.py. Run from this skill folder: python3 -m unittest discover -s tests"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent / "audit.py"

DESIGN = """---
name: Fixture
colors:
  text: '#111927'
  border: '#EEEEEE'
---

# DESIGN.md
"""


def run_audit(files, design=DESIGN):
    """Write `files` (relative path -> content) into a temp project and audit it."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        if design is not None:
            (root / "DESIGN.md").write_text(design)
        for rel, content in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        out = root / "report.json"
        subprocess.run(
            [sys.executable, str(AUDIT), "--root", str(root), "--json", str(out)],
            check=True, capture_output=True, text=True,
        )
        return json.loads(out.read_text())


def row(report, hexv, translucent=False):
    found = [r for r in report["rows"] if r["hex"] == hexv and r["alpha"] is translucent]
    return found[0] if found else None


class NamedColors(unittest.TestCase):
    def test_named_color_in_stylesheet_is_a_literal(self):
        report = run_audit({"src/a.module.scss": ".a { border: 1px solid lightgray; }\n"})
        r = row(report, "#d3d3d3")
        self.assertIsNotNone(r)
        self.assertEqual(r["uses"], 1)
        self.assertEqual(r["named"], ["lightgray"])
        self.assertEqual(report["literal_colors"]["named_uses"], 1)
        self.assertEqual(report["stylesheet_coverage"]["color"].get("literal"), 1)

    def test_named_color_in_script_strings_any_case_and_multiline(self):
        report = run_audit({"src/A.tsx": (
            "const a = { borderColor: 'lightGrey' }\n"
            "const b = { border: '1px solid lightgray !important' }\n"
            "const c = {\n"
            "  backgroundColor: preview\n"
            "    ? 'grey.900'\n"
            "    : active\n"
            "      ? 'lightgray'\n"
            "      : 'transparent',\n"
            "}\n"
            "const d = <path fill=\"black\" />\n"
        )})
        self.assertEqual(row(report, "#d3d3d3")["uses"], 3)
        self.assertEqual(row(report, "#d3d3d3")["named"], ["lightgray", "lightgrey"])
        self.assertEqual(row(report, "#000000")["uses"], 1)
        self.assertIsNone(row(report, "#808080"))  # 'grey.900' is a palette key

    def test_color_words_outside_color_values_are_ignored(self):
        report = run_audit({
            "src/a.module.scss": (
                ".white { color: var(--white-base); }\n"
                ".b { color: $black; background: colors.$auth-color-white; }\n"
            ),
            "src/A.tsx": (
                "const title = 'Black Friday'\n"
                "const cls = { className: 'text-red-500' }\n"
                "const c = { color: red }\n"
            ),
        })
        self.assertEqual(report["rows"], [])

    def test_named_color_definition_counts_as_token_definition(self):
        report = run_audit({"src/styles/_palette.scss": (
            "$input-border: lightgray;\n$title: #123456;\n"
        )})
        missing = {m["hex"] for m in report["defined_in_code_missing_in_design_md"]}
        self.assertIn("#d3d3d3", missing)


class Translucent(unittest.TestCase):
    def test_translucent_black_is_not_counted_as_opaque_black(self):
        report = run_audit({"src/a.module.scss": (
            ".a { color: #000; }\n"
            ".b { background-color: rgba(0, 0, 0, 0.6); }\n"
            ".c { background-color: rgba(0,0,0,.5); }\n"
            ".d { color: rgb(0, 0, 0); }\n"
            ".e { color: rgba(0, 0, 0, 1); }\n"
        )})
        self.assertEqual(row(report, "#000000")["uses"], 3)
        self.assertEqual(row(report, "#000000", translucent=True)["uses"], 2)
        self.assertEqual(row(report, "#000000", translucent=True)["band"], "translucent")
        self.assertEqual(report["literal_colors"]["translucent"], {"unique": 1, "uses": 2})

    def test_other_translucent_notations(self):
        report = run_audit({
            "src/a.module.scss": (
                ".a { background: #54545480; }\n"
                ".b { background: rgba(#545454, 0.5); }\n"
                ".c { background: rgb(84 84 84 / 50%); }\n"
            ),
            "src/A.ts": "const a = { backgroundColor: alpha('#545454', 0.38) }\n",
        })
        self.assertIsNone(row(report, "#545454"))
        self.assertEqual(row(report, "#545454", translucent=True)["uses"], 4)

    def test_translucent_colors_stay_out_of_bands_and_clusters(self):
        report = run_audit({"src/a.module.scss": (
            ".a { background-color: rgba(0, 0, 0, 0.6); }\n"
        )})
        self.assertEqual(report["bands"]["uses"], {"translucent": 1})
        self.assertEqual(report["far_color_clusters"]["count"], 0)

    def test_translucent_definition_is_not_a_token_definition(self):
        report = run_audit({"src/styles/variables.scss": (
            ":root {\n  --disabled-bg: #54545480;\n  --divider: rgba(217, 217, 217, 0.5);\n"
            "  --title: #123456;\n}\n"
        )})
        missing = {m["hex"] for m in report["defined_in_code_missing_in_design_md"]}
        self.assertEqual(missing, {"#123456"})
        self.assertEqual(
            sorted(d["hex"] for d in report["translucent_definitions"]), ["#545454", "#d9d9d9"])


class Roles(unittest.TestCase):
    def test_rows_report_the_role_each_literal_is_used_in(self):
        report = run_audit({
            "src/a.module.scss": (
                ".a { color: #565656; }\n"
                ".b { background-color: #565656; }\n"
                ".c { border: 1px solid #565656; }\n"
            ),
            "src/A.tsx": "const a = { borderColor: '#565656' }\nconst b = <path fill=\"#565656\" />\n",
        })
        self.assertEqual(
            row(report, "#565656")["roles"], {"text": 1, "surface": 1, "border": 2, "icon": 1})


if __name__ == "__main__":
    unittest.main()
