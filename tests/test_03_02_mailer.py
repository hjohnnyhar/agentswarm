"""
Tests for plan 03-02: Mailer agent (src/agents/mailer.py)

TDD RED phase — written before implementation exists.
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open

# Set a dummy ANTHROPIC_API_KEY so Config doesn't raise at import time
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.types import WorkflowContext
from src.config import Config


def make_config(app_password="secret", gmail_address="sender@gmail.com", recipient="recv@gmail.com"):
    """Build a Config with controlled credentials (bypasses __post_init__ env checks)."""
    c = Config.__new__(Config)
    c.anthropic_api_key = "test-key"
    c.gmail_address = gmail_address
    c.recipient_email = recipient
    c.gmail_app_password = app_password
    return c


def make_ctx(topic="AI Safety", pdf_path="output/whitepaper.pdf", feedback="Looks good."):
    ctx = WorkflowContext(topic=topic, published_pdf_path=pdf_path)
    ctx.review_feedback = feedback
    return ctx


class TestMailerGuardClauses(unittest.TestCase):

    def test_raises_environment_error_when_app_password_empty(self):
        """Should raise EnvironmentError when gmail_app_password is empty string."""
        from src.agents.mailer import run_mailer
        ctx = make_ctx()
        config = make_config(app_password="")
        with self.assertRaises(EnvironmentError) as cm:
            run_mailer(ctx, config)
        self.assertIn("GMAIL_APP_PASSWORD", str(cm.exception))

    def test_environment_error_message_contains_helpful_hint(self):
        """Error message should tell user where to get an app password."""
        from src.agents.mailer import run_mailer
        ctx = make_ctx()
        config = make_config(app_password="")
        with self.assertRaises(EnvironmentError) as cm:
            run_mailer(ctx, config)
        msg = str(cm.exception)
        # Should mention where to generate the password
        self.assertTrue(
            "myaccount.google.com" in msg or "App password" in msg or "app password" in msg,
            f"Expected helpful hint in error, got: {msg}"
        )

    def test_raises_file_not_found_when_pdf_missing(self):
        """Should raise FileNotFoundError when published_pdf_path does not exist."""
        from src.agents.mailer import run_mailer
        ctx = make_ctx(pdf_path="/nonexistent/path/whitepaper.pdf")
        config = make_config(app_password="valid-password")
        with self.assertRaises(FileNotFoundError) as cm:
            run_mailer(ctx, config)
        self.assertIn("/nonexistent/path/whitepaper.pdf", str(cm.exception))

    def test_environment_error_checked_before_file_check(self):
        """Guard clause order: password check must come before file existence check."""
        from src.agents.mailer import run_mailer
        ctx = make_ctx(pdf_path="/nonexistent/path/whitepaper.pdf")
        config = make_config(app_password="")
        # Should raise EnvironmentError (not FileNotFoundError) even with missing PDF
        with self.assertRaises(EnvironmentError):
            run_mailer(ctx, config)


class TestMailerEmailConstruction(unittest.TestCase):

    def _run_with_mock_smtp(self, ctx, config):
        """Helper: run run_mailer with SMTP mocked out, capturing send_message calls."""
        from src.agents.mailer import run_mailer

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"%PDF-1.4 fake pdf content")
            pdf_path = tmp.name

        ctx.published_pdf_path = pdf_path

        sent_messages = []

        mock_server = MagicMock()
        mock_server.send_message.side_effect = lambda msg: sent_messages.append(msg)

        mock_smtp_cls = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        try:
            with patch("smtplib.SMTP", mock_smtp_cls):
                result = run_mailer(ctx, config)
        finally:
            os.unlink(pdf_path)

        return result, sent_messages, mock_server

    def test_returns_ctx_unchanged(self):
        """run_mailer is side-effect only — returns ctx."""
        ctx = make_ctx(topic="Quantum Computing", feedback="Strong work.")
        config = make_config()
        result, _, _ = self._run_with_mock_smtp(ctx, config)
        self.assertIs(result, ctx)

    def test_smtp_host_and_port(self):
        """Must connect to smtp.gmail.com on port 587."""
        ctx = make_ctx()
        config = make_config()
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)

        from src.agents.mailer import run_mailer
        import smtplib

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"%PDF-1.4 fake")
            pdf_path = tmp.name
        ctx.published_pdf_path = pdf_path

        mock_server2 = MagicMock()
        call_args = {}

        class CapturingSMTP:
            def __init__(self, host, port):
                call_args["host"] = host
                call_args["port"] = port

            def __enter__(self):
                return mock_server2

            def __exit__(self, *a):
                return False

        try:
            with patch("smtplib.SMTP", CapturingSMTP):
                run_mailer(ctx, config)
        finally:
            os.unlink(pdf_path)

        self.assertEqual(call_args.get("host"), "smtp.gmail.com")
        self.assertEqual(call_args.get("port"), 587)

    def test_starttls_called(self):
        """STARTTLS must be called before login."""
        ctx = make_ctx()
        config = make_config()
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        mock_server.starttls.assert_called_once()

    def test_login_with_address_and_password(self):
        """Login must use gmail_address and gmail_app_password."""
        ctx = make_ctx()
        config = make_config(app_password="myAppPass", gmail_address="me@gmail.com")
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        mock_server.login.assert_called_once_with("me@gmail.com", "myAppPass")

    def test_send_message_called_once(self):
        """send_message must be called exactly once."""
        ctx = make_ctx()
        config = make_config()
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        mock_server.send_message.assert_called_once()

    def test_email_subject_contains_topic(self):
        """Subject must be 'White Paper: {topic}'."""
        ctx = make_ctx(topic="Renewable Energy")
        config = make_config()
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg["Subject"], "White Paper: Renewable Energy")

    def test_email_from_address(self):
        """From header must match config.gmail_address."""
        ctx = make_ctx()
        config = make_config(gmail_address="sender@gmail.com")
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg["From"], "sender@gmail.com")

    def test_email_to_address(self):
        """To header must match config.recipient_email."""
        ctx = make_ctx()
        config = make_config(recipient="boss@example.com")
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg["To"], "boss@example.com")

    def test_email_body_contains_topic_and_feedback(self):
        """Body must contain topic and review_feedback."""
        ctx = make_ctx(topic="Space Exploration", feedback="Excellent research depth.")
        config = make_config()
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        msg = mock_server.send_message.call_args[0][0]
        body = msg.get_payload(0).get_payload()
        self.assertIn("Space Exploration", body)
        self.assertIn("Excellent research depth.", body)

    def test_email_has_pdf_attachment(self):
        """Email must have a PDF attachment named whitepaper.pdf."""
        ctx = make_ctx()
        config = make_config()
        _, _, mock_server = self._run_with_mock_smtp(ctx, config)
        msg = mock_server.send_message.call_args[0][0]
        payload = msg.get_payload()
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 1, "Expected multipart message with attachment")
        attachment = payload[1]
        content_disp = attachment.get("Content-Disposition", "")
        self.assertIn("whitepaper.pdf", content_disp)


class TestMailerConsoleOutput(unittest.TestCase):

    def test_prints_confirmation_on_success(self, capsys=None):
        """Should print '[Mailer] Email sent to ...' on success."""
        from src.agents.mailer import run_mailer
        import io

        ctx = make_ctx(topic="Biotech")
        config = make_config(recipient="user@example.com")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"%PDF fake")
            pdf_path = tmp.name
        ctx.published_pdf_path = pdf_path

        mock_server = MagicMock()
        mock_smtp_cls = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        import sys
        captured = io.StringIO()
        sys.stdout = captured

        try:
            with patch("smtplib.SMTP", mock_smtp_cls):
                run_mailer(ctx, config)
        finally:
            sys.stdout = sys.__stdout__
            os.unlink(pdf_path)

        output = captured.getvalue()
        self.assertIn("[Mailer]", output)
        self.assertIn("user@example.com", output)
        self.assertIn("Biotech", output)

    def test_prints_error_and_reraises_on_smtp_failure(self):
        """Should print '[Mailer] ERROR: ...' and re-raise on SMTP exception."""
        from src.agents.mailer import run_mailer
        import smtplib
        import io

        ctx = make_ctx(topic="Nanotechnology")
        config = make_config()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"%PDF fake")
            pdf_path = tmp.name
        ctx.published_pdf_path = pdf_path

        mock_server = MagicMock()
        mock_server.send_message.side_effect = smtplib.SMTPException("Connection refused")
        mock_smtp_cls = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        import sys
        captured = io.StringIO()
        sys.stdout = captured

        try:
            with patch("smtplib.SMTP", mock_smtp_cls):
                with self.assertRaises(Exception):
                    run_mailer(ctx, config)
        finally:
            sys.stdout = sys.__stdout__
            os.unlink(pdf_path)

        output = captured.getvalue()
        self.assertIn("[Mailer] ERROR", output)


class TestMailerNoNewDependencies(unittest.TestCase):

    def test_only_stdlib_imports(self):
        """mailer.py must not import any third-party packages."""
        import ast
        mailer_path = os.path.join(os.path.dirname(__file__), "..", "src", "agents", "mailer.py")
        with open(mailer_path) as f:
            tree = ast.parse(f.read())

        stdlib_allowed = {
            "os", "smtplib", "email", "email.mime", "email.mime.multipart",
            "email.mime.text", "email.mime.application", "typing"
        }
        third_party_prefixes = {
            "anthropic", "pandas", "numpy", "reportlab", "matplotlib",
            "dotenv", "requests", "flask", "django", "fastapi", "pytest",
            "psycopg2", "sqlalchemy", "dash", "plotly"
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for prefix in third_party_prefixes:
                        self.assertFalse(
                            alias.name.startswith(prefix),
                            f"Third-party import found: {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for prefix in third_party_prefixes:
                    self.assertFalse(
                        module.startswith(prefix),
                        f"Third-party import found: from {module}"
                    )


if __name__ == "__main__":
    unittest.main()
