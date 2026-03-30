"""
Test that benign prompts do not trigger any InferenceWall signatures.

Loads a corpus of 50 diverse, clearly benign prompts and asserts that the
detection pipeline returns a score of 0 for every single one — i.e. zero
false positives.
"""

from pathlib import Path

import pytest
import yaml

from inferwall.core.pipeline import Pipeline

CORPUS_PATH = Path(__file__).parent.parent / "corpus" / "benign_prompts.yaml"


@pytest.fixture(scope="module")
def pipeline():
    return Pipeline()


@pytest.fixture(scope="module")
def benign_prompts():
    data = yaml.safe_load(CORPUS_PATH.read_text())
    return data["prompts"]


def test_benign_corpus_no_false_positives(pipeline, benign_prompts):
    """Every prompt in the benign corpus must produce score == 0."""
    false_positives = []
    for item in benign_prompts:
        result = pipeline.scan_input(item["text"])
        if result.score > 0:
            false_positives.append(
                {
                    "text": item["text"],
                    "category": item["category"],
                    "score": result.score,
                    "matches": result.matches,
                }
            )
    assert len(false_positives) == 0, (
        f"{len(false_positives)} false positive(s) detected:\n"
        + "\n".join(
            f"  [{fp['category']}] score={fp['score']} text={fp['text']!r}"
            for fp in false_positives
        )
    )


def test_benign_corpus_has_50_prompts(benign_prompts):
    """Sanity-check: the corpus file should contain exactly 50 prompts."""
    assert len(benign_prompts) == 50


def test_benign_corpus_covers_all_categories(benign_prompts):
    """Sanity-check: all expected categories are represented."""
    categories = {item["category"] for item in benign_prompts}
    expected = {"casual", "technical", "creative", "business", "multilingual"}
    assert categories == expected, f"Missing categories: {expected - categories}"
