"""Regression tests for cryptocurrency wallet address leakage signatures."""

from __future__ import annotations

import re
from pathlib import Path

from inferwall.signatures.loader import SignatureLoader

CATALOG_DIR = Path(__file__).parent.parent.parent / "src" / "inferwall" / "catalog"
SIGNATURE_ID = "DL-P-009"


def _crypto_patterns() -> list[re.Pattern[str]]:
    loader = SignatureLoader(CATALOG_DIR)
    loader.load()
    sig = loader.get_by_id(SIGNATURE_ID)

    assert sig is not None
    assert sig.detection.patterns is not None
    return [re.compile(pattern.value or "") for pattern in sig.detection.patterns]


def _matches_any_pattern(text: str) -> bool:
    return any(pattern.search(text) for pattern in _crypto_patterns())


def test_crypto_wallet_signature_matches_common_wallet_formats() -> None:
    examples = [
        "Send the refund to 0x52908400098527886E0F7030069857D2E4169EE7.",
        "Bitcoin payout address: 1BoatSLRHtKNngkdXEeobR76b53LETtpyT.",
        "BTC bech32 address: bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080.",
        "Solana wallet: 4Nd1mJ8mXH7UzWuh8VZpFqqY5nC8YZvD4n8C5X2Qw3hA.",
    ]

    for example in examples:
        assert _matches_any_pattern(example)


def test_crypto_wallet_signature_avoids_common_non_wallet_strings() -> None:
    examples = [
        "The transaction fee is 0.005 ETH and chain id is 1.",
        "The UUID is 550e8400-e29b-41d4-a716-446655440000.",
        "The SHA-256 prefix is 9f86d081884c7d659a2feaa0c55ad015.",
        "Contact support with ticket TB-2026-04-28-0001.",
    ]

    for example in examples:
        assert not _matches_any_pattern(example)
