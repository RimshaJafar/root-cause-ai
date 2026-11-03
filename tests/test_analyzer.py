
import unittest

from app.analyzer import analyze_traceback


SAMPLE_TRACEBACK = """Traceback (most recent call last):
  File "app/auth.py", line 42, in login
    user_id = user.id
AttributeError: 'NoneType' object has no attribute 'id'
"""


class TestAnalyzeTraceback(unittest.TestCase):

    def test_extracts_exception(self):
        result = analyze_traceback(SAMPLE_TRACEBACK)

        self.assertEqual(
            result["exception_type"],
            "AttributeError",
        )

        self.assertEqual(
            result["message"],
            "'NoneType' object has no attribute 'id'",
        )

    def test_extracts_location(self):
        result = analyze_traceback(SAMPLE_TRACEBACK)

        self.assertEqual(
            result["last_frame"],
            {
                "file": "app/auth.py",
                "line": 42,
                "function": "login",
            },
        )

    def test_empty_traceback_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_traceback("")


if __name__ == "__main__":
    unittest.main()
