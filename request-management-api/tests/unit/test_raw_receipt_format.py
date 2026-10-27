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

    @classmethod
    def setUpClass(cls):
        tree = ast.parse(MODEL.read_text(encoding="utf-8-sig"))
        model = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "FOIRawRequest"
        )
        cls.query = next(
            node for node in model.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "getbasequery"
        )

    def assignment(self, name):
        return next(
            node.value
            for node in self.query.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == name
                for target in node.targets
            )
        )

    def test_fallback_uses_correct_postgresql_date_masks(self):
        for name, expected_mask in (
            ("receiveddate", "YYYY-MM-DD"),
            ("receiveddateuf", "YYYY-MM-DD HH24:MI:SS"),
        ):
            with self.subTest(field=name):
                expression = self.assignment(name)
                calls = [
                    node for node in ast.walk(expression)
                    if isinstance(node, ast.Call)
                    and ast.unparse(node.func) == "func.to_char"
                ]
                self.assertEqual(len(calls), 1)
                self.assertEqual(
                    ast.unparse(calls[0].args[0]),
                    "created_at_vancouver",
                )
                self.assertEqual(calls[0].args[1].value, expected_mask)

    def test_conversion_preserves_history_and_permanent_utc_minus_seven(self):
        expression = ast.unparse(self.assignment("created_at_vancouver"))

        self.assertIn(
            "FOIRawRequest.created_at >= datetime(2026, 11, 1, 9, 0, 0)",
            expression,
        )
        self.assertIn(
            "func.timezone('PDT', func.timezone('UTC', FOIRawRequest.created_at))",
            expression,
        )
        self.assertIn(
            "else_=func.timezone('America/Vancouver', "
            "func.timezone('UTC', FOIRawRequest.created_at))",
            expression,
        )

    def test_saved_receipt_fields_still_pass_through(self):
        for name, field in (
            ("receiveddate", "receivedDate"),
            ("receiveddateuf", "receivedDateUF"),
        ):
            with self.subTest(field=field):
                expression = ast.unparse(self.assignment(name))
                self.assertIn(
                    "else_=func.nullif("
                    f"FOIRawRequest.requestrawdata['{field}'].astext, '')",
                    expression,
                )


if __name__ == "__main__":
    unittest.main()