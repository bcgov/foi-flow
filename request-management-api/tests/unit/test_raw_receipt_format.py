import ast
import unittest
from pathlib import Path


MODEL = (
    Path(__file__).resolve().parents[2]
    / "request_api"
    / "models"
    / "FOIRawRequests.py"
)


class RawReceiptFormatTests(unittest.TestCase):

    def test_fallback_uses_correct_postgresql_date_masks(self):
        tree = ast.parse(MODEL.read_text(encoding="utf-8-sig"))

        model = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "FOIRawRequest"
        )

        query = next(
            node for node in model.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "getbasequery"
        )

        masks = []

        for node in ast.walk(query):
            if not isinstance(node, ast.Call):
                continue

            if ast.unparse(node.func) != "func.to_char":
                continue

            if len(node.args) != 2:
                continue

            if ast.unparse(node.args[0]) != "FOIRawRequest.created_at":
                continue

            self.assertIsInstance(node.args[1], ast.Constant)
            masks.append(node.args[1].value)

        self.assertCountEqual(
            masks,
            [
                "YYYY-MM-DD",
                "YYYY-MM-DD HH24:MI:SS",
            ],
        )


if __name__ == "__main__":
    unittest.main()