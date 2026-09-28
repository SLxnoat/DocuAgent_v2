"""Markdown Validation and Quality Scoring Tools for QA and Compliance micro-crews."""

import re
import json
from typing import List, Dict, Any, Optional, Type, Union
from pydantic import BaseModel, Field

try:
    from crewai.tools import BaseTool as CrewAIBaseTool
except ImportError:
    CrewAIBaseTool = object


class MarkdownValidatorInput(BaseModel):
    """Input schema for MarkdownValidatorTool."""

    raw_markdown: str = Field(description="Generated raw markdown text of the manual")
    expected_steps_count: Optional[int] = Field(
        default=None,
        description="Expected minimum number of procedural steps",
    )


class MarkdownValidatorTool(CrewAIBaseTool if CrewAIBaseTool is not object else BaseModel):
    """Tool that validates Markdown structure, headings, step numbering, and screenshot references."""

    name: str = "MarkdownValidatorTool"
    description: str = (
        "Validates technical documentation Markdown for structural integrity, correct heading hierarchy "
        "(H1 -> H2 -> H3), chronological step numbering continuity, and valid embedded screenshot syntax."
    )
    args_schema: Type[BaseModel] = MarkdownValidatorInput

    def validate_markdown(
        self,
        raw_markdown: str,
        expected_steps_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Perform deterministic syntactic and structural validation on markdown."""
        issues: List[str] = []
        warnings: List[str] = []

        if not raw_markdown or not raw_markdown.strip():
            return {
                "is_valid": False,
                "issues": ["Markdown document is completely empty."],
                "warnings": [],
                "detected_steps": 0,
                "has_h1": False,
                "has_executive_summary": False,
                "has_prerequisites": False,
            }

        lines = raw_markdown.splitlines()

        # 1. Heading 1 check
        has_h1 = any(line.strip().startswith("# ") for line in lines)
        if not has_h1:
            issues.append("Missing top-level title heading (# Title).")

        # 2. Executive Summary check
        has_summary = any(
            re.search(r"##\s+(Executive Summary|Overview|Summary|Introduction)", line, re.IGNORECASE)
            for line in lines
        )
        if not has_summary:
            warnings.append("Missing 'Executive Summary' or 'Overview' section (## Executive Summary).")

        # 3. Prerequisites check
        has_prereqs = any(
            re.search(r"##\s+(Prerequisites|Requirements|Before You Begin)", line, re.IGNORECASE)
            for line in lines
        )
        if not has_prereqs:
            warnings.append("Missing 'Prerequisites' section (## Prerequisites).")

        # 4. Step Numbering continuity
        step_matches = []
        for idx, line in enumerate(lines):
            match = re.search(r"###\s+Step\s+(\d+)\s*:", line, re.IGNORECASE)
            if match:
                step_matches.append(int(match.group(1)))

        detected_steps = len(step_matches)
        if expected_steps_count and detected_steps < expected_steps_count:
            issues.append(
                f"Expected at least {expected_steps_count} steps, but only found {detected_steps} step headings."
            )

        # Check step continuity (e.g. 1, 2, 3...)
        for i, num in enumerate(step_matches, 1):
            if num != i:
                issues.append(f"Step sequence broken: Expected Step {i}, but found Step {num}.")
                break

        # 5. Image reference check
        image_count = len(re.findall(r"!\[.*?\]\(.*?\)", raw_markdown))

        is_valid = len(issues) == 0
        return {
            "is_valid": is_valid,
            "detected_steps": detected_steps,
            "embedded_images_count": image_count,
            "has_h1": has_h1,
            "has_executive_summary": has_summary,
            "has_prerequisites": has_prereqs,
            "issues": issues,
            "warnings": warnings,
        }

    def _run(
        self,
        raw_markdown: str,
        expected_steps_count: Optional[int] = None,
    ) -> str:
        res = self.validate_markdown(raw_markdown, expected_steps_count)
        return json.dumps(res, indent=2)

    def run(
        self,
        raw_markdown: str,
        expected_steps_count: Optional[int] = None,
    ) -> str:
        return self._run(raw_markdown, expected_steps_count)


class QualityScoreInput(BaseModel):
    """Input schema for QualityScoreCalculatorTool."""

    raw_markdown: str = Field(description="Raw markdown document")
    synthesized_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Synthesized steps list")
    validation_results: Optional[Dict[str, Any]] = Field(default=None, description="Output from MarkdownValidatorTool")


class QualityScoreCalculatorTool(CrewAIBaseTool if CrewAIBaseTool is not object else BaseModel):
    """Tool that computes weighted quality scores, identifies gaps, and produces QA scorecard."""

    name: str = "QualityScoreCalculatorTool"
    description: str = (
        "Calculates an objective weighted quality score (0-100%) evaluating completeness (35%), "
        "clarity (35%), and structure (30%). Determines approval gate status (Score >= 85)."
    )
    args_schema: Type[BaseModel] = QualityScoreInput

    def compute_scorecard(
        self,
        raw_markdown: str,
        synthesized_steps: List[Dict[str, Any]],
        validation_results: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate weighted score and actionable suggestions."""
        validator = MarkdownValidatorTool()
        val = validation_results or validator.validate_markdown(raw_markdown)

        completeness = 100.0
        clarity = 100.0
        structure = 100.0
        suggestions: List[str] = []
        missing_items: List[str] = []
        strengths: List[str] = []

        # Completeness deductions
        if not val.get("has_executive_summary"):
            completeness -= 20.0
            missing_items.append("Executive Summary section")
            suggestions.append("Add an Executive Summary section explaining workflow objectives.")
        else:
            strengths.append("Contains structured executive overview.")

        if not val.get("has_prerequisites"):
            completeness -= 15.0
            missing_items.append("Prerequisites section")
            suggestions.append("Specify prerequisites or credentials needed to execute the workflow.")
        else:
            strengths.append("Specifies prerequisite conditions.")

        if not synthesized_steps:
            completeness -= 50.0
            missing_items.append("Procedural steps")
            suggestions.append("Synthesize numbered step-by-step procedural actions.")

        # Structure deductions
        if not val.get("has_h1"):
            structure -= 20.0
            suggestions.append("Include a clear H1 document title.")

        for issue in val.get("issues", []):
            structure -= 15.0
            suggestions.append(f"Resolve structural issue: {issue}")

        if val.get("embedded_images_count", 0) > 0:
            strengths.append(f"Includes {val['embedded_images_count']} embedded visual screenshot references.")
        else:
            structure -= 10.0
            suggestions.append("Embed visual screenshots with callouts for user guidance.")

        # Clarity evaluations
        short_steps = [s for s in synthesized_steps if len(s.get("instruction", "")) < 15]
        if short_steps:
            clarity -= 15.0
            suggestions.append("Expand terse step instructions into clear imperative sentences.")
        else:
            strengths.append("Step instructions are clear and descriptive.")

        # Clamp individual sub-scores
        completeness = max(0.0, min(100.0, completeness))
        clarity = max(0.0, min(100.0, clarity))
        structure = max(0.0, min(100.0, structure))

        # Weighted aggregate score
        overall_score = round(
            (completeness * 0.35) + (clarity * 0.35) + (structure * 0.30),
            1,
        )
        is_approved = overall_score >= 85.0 and len(missing_items) == 0

        return {
            "score": overall_score,
            "is_approved": is_approved,
            "completeness_score": completeness,
            "clarity_score": clarity,
            "structure_score": structure,
            "strengths": strengths,
            "suggestions": suggestions,
            "missing_items": missing_items,
        }

    def _run(
        self,
        raw_markdown: str,
        synthesized_steps: List[Dict[str, Any]],
        validation_results: Optional[Dict[str, Any]] = None,
    ) -> str:
        scorecard = self.compute_scorecard(
            raw_markdown=raw_markdown,
            synthesized_steps=synthesized_steps,
            validation_results=validation_results,
        )
        return json.dumps(scorecard, indent=2)

    def run(
        self,
        raw_markdown: str,
        synthesized_steps: List[Dict[str, Any]],
        validation_results: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self._run(
            raw_markdown=raw_markdown,
            synthesized_steps=synthesized_steps,
            validation_results=validation_results,
        )
