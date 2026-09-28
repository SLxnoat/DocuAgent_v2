"""Security validation tests using standard unittest."""

import unittest
from app.core.security import (
    validate_target_url,
    sanitize_identifier,
    mask_sensitive_value,
    SecurityValidationError,
)


class TestSecurity(unittest.TestCase):
    def test_validate_target_url_valid(self):
        self.assertEqual(validate_target_url("https://example.com/app"), "https://example.com/app")
        self.assertEqual(validate_target_url("http://app.internal.corp"), "http://app.internal.corp")

    def test_validate_target_url_disallowed_schemes(self):
        with self.assertRaises(SecurityValidationError):
            validate_target_url("file:///etc/passwd")

        with self.assertRaises(SecurityValidationError):
            validate_target_url("gopher://127.0.0.1:6379")

    def test_validate_target_url_cloud_metadata(self):
        with self.assertRaises(SecurityValidationError):
            validate_target_url("http://169.254.169.254/latest/meta-data/")

        with self.assertRaises(SecurityValidationError):
            validate_target_url("http://metadata.google.internal/computeMetadata/v1/")

    def test_sanitize_identifier_path_traversal(self):
        self.assertEqual(sanitize_identifier("sess_1234567890"), "sess_1234567890")
        self.assertEqual(sanitize_identifier("doc-abc_123"), "doc-abc_123")

        with self.assertRaises(SecurityValidationError):
            sanitize_identifier("../../etc/passwd")

        with self.assertRaises(SecurityValidationError):
            sanitize_identifier("sess; rm -rf /")

    def test_mask_sensitive_value(self):
        self.assertEqual(mask_sensitive_value("user_password", "password", "SuperSecret123"), "••••••••")
        self.assertEqual(mask_sensitive_value("api_key", "text", "sk-1234567890"), "••••••••")
        self.assertEqual(mask_sensitive_value("username", "text", "john_doe"), "john_doe")


if __name__ == "__main__":
    unittest.main()
