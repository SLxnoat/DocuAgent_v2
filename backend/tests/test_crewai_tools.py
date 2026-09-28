"""Unit tests for Phase 2 Custom CrewAI & Multi-Agent Tools."""

import unittest
from app.agents.common.tools.dom_parser import DOMTraceParserTool
from app.agents.common.tools.markdown_qa import MarkdownValidatorTool, QualityScoreCalculatorTool


class TestCrewAITools(unittest.TestCase):
    """Test suite for custom Pydantic tools."""

    def setUp(self):
        self.dom_parser = DOMTraceParserTool()
        self.md_validator = MarkdownValidatorTool()
        self.qa_calculator = QualityScoreCalculatorTool()

    def test_dom_trace_parser_denoising_and_grouping(self):
        """Test that DOMTraceParserTool filters hovers/scrolls and coalesces consecutive inputs."""
        sample_traces = [
            {
                "id": "act_1",
                "action_type": "hover",
                "page_title": "Login Page",
                "page_url": "https://example.com/login",
                "target_element": {"css_selector": "button.login-btn", "inner_text": "Login"},
            },
            {
                "id": "act_2",
                "action_type": "scroll",
                "page_title": "Login Page",
                "page_url": "https://example.com/login",
            },
            {
                "id": "act_3",
                "action_type": "input",
                "input_value": "user@",
                "page_title": "Login Page",
                "page_url": "https://example.com/login",
                "target_element": {
                    "css_selector": "input#email",
                    "placeholder": "Enter your email",
                    "tag_name": "input",
                },
                "screenshot_url": "/storage/screenshots/shot1.jpg",
            },
            {
                "id": "act_4",
                "action_type": "input",
                "input_value": "user@example.com",
                "page_title": "Login Page",
                "page_url": "https://example.com/login",
                "target_element": {
                    "css_selector": "input#email",
                    "placeholder": "Enter your email",
                    "tag_name": "input",
                },
                "screenshot_url": "/storage/screenshots/shot2.jpg",
            },
            {
                "id": "act_5",
                "action_type": "input",
                "input_value": "supersecretpassword",
                "page_title": "Login Page",
                "page_url": "https://example.com/login",
                "target_element": {
                    "css_selector": "input#password",
                    "input_type": "password",
                    "tag_name": "input",
                },
            },
            {
                "id": "act_6",
                "action_type": "click",
                "page_title": "Login Page",
                "page_url": "https://example.com/login",
                "target_element": {
                    "css_selector": "button#submit-btn",
                    "inner_text": "Sign In",
                    "tag_name": "button",
                },
            },
        ]

        result = self.dom_parser.parse_traces(sample_traces, filter_noise=True)
        
        self.assertEqual(result["total_raw_traces"], 6)
        # Should coalesce into 3 steps: Email input, Password input, Sign In click
        self.assertEqual(result["parsed_steps_count"], 3)
        
        steps = result["grouped_steps"]
        # Step 1: Coalesced email input
        self.assertEqual(steps[0]["primary_action"], "input")
        self.assertEqual(steps[0]["input_value"], "user@example.com")
        self.assertIn("act_3", steps[0]["raw_action_ids"])
        self.assertIn("act_4", steps[0]["raw_action_ids"])
        
        # Step 2: Sensitive password redacted
        self.assertTrue(steps[1]["is_sensitive"])
        self.assertEqual(steps[1]["input_value"], "•••••••• [REDACTED]")
        
        # Step 3: Button click
        self.assertEqual(steps[2]["primary_action"], "click")
        self.assertIn("Sign In", steps[2]["title"])

    def test_markdown_validator_tool(self):
        """Test structural checks and heading continuity."""
        valid_md = """# User Management Guide

## Executive Summary
This document guides users through adding and configuring accounts.

## Prerequisites
- Administrative credentials
- Valid web session

### Step 1: Navigate to Dashboard
Log in and access the administration console.
![Step 1](/storage/screenshots/step_1.jpg)

### Step 2: Click Add User
Click the primary action button to register a new user.
![Step 2](/storage/screenshots/step_2.jpg)
"""
        res = self.md_validator.validate_markdown(valid_md)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["detected_steps"], 2)
        self.assertTrue(res["has_h1"])
        self.assertTrue(res["has_executive_summary"])
        self.assertTrue(res["has_prerequisites"])

        # Invalid MD missing H1 and broken step order
        invalid_md = """### Step 2: Broken Step
Missing title and summary
"""
        invalid_res = self.md_validator.validate_markdown(invalid_md)
        self.assertFalse(invalid_res["is_valid"])
        self.assertFalse(invalid_res["has_h1"])
        self.assertTrue(any("Step sequence broken" in issue for issue in invalid_res["issues"]))


    def test_quality_score_calculator(self):
        """Test quality scorecard generation and approval gate threshold (Score >= 85)."""
        valid_md = """# User Guide
## Executive Summary
Comprehensive walkthrough of the portal.
## Prerequisites
- Valid account

### Step 1: Login
Navigate to login page and submit your credentials.
![Step 1](/img/step1.jpg)

### Step 2: Dashboard
Select settings from sidebar navigation.
![Step 2](/img/step2.jpg)
"""
        steps = [
            {"step_number": 1, "title": "Login", "instruction": "Navigate to login page and submit your credentials."},
            {"step_number": 2, "title": "Dashboard", "instruction": "Select settings from sidebar navigation."},
        ]

        scorecard = self.qa_calculator.compute_scorecard(raw_markdown=valid_md, synthesized_steps=steps)
        self.assertGreaterEqual(scorecard["score"], 85.0)
        self.assertTrue(scorecard["is_approved"])
        self.assertEqual(len(scorecard["missing_items"]), 0)


if __name__ == "__main__":
    unittest.main()
