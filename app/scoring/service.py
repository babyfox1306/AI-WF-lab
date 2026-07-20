"""Scorecard system for transparent, deterministic scoring."""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


SCORE_VERSION = "1.0"

DEFAULT_WEIGHTS = {
    "technical_fit": 0.30,
    "proof_strength": 0.20,
    "client_quality": 0.15,
    "scope_clarity": 0.10,
    "budget_fit": 0.10,
    "competition_risk": 0.10,
    "delivery_confidence": 0.05,
}

DEFAULT_THRESHOLDS = {
    "bid": 75,
    "conditional_bid": 55,
    "skip": 0,
}


@dataclass
class ScoreInput:
    """Input scores from individual agents (0-100 scale)."""

    technical_fit: float = 50.0
    proof_strength: float = 50.0
    client_quality: float = 50.0
    scope_clarity: float = 50.0
    budget_fit: float = 50.0
    competition_risk: float = 50.0  # Higher = less competition (better)
    delivery_confidence: float = 50.0


@dataclass
class ScoreResult:
    """Result of score calculation."""

    total: float
    categories: Dict[str, float]
    weights: Dict[str, float]
    weighted_scores: Dict[str, float]
    decision: str
    score_version: str = SCORE_VERSION
    thresholds: Dict[str, int] = field(default_factory=lambda: dict(DEFAULT_THRESHOLDS))


class ScoreCalculator:
    """Deterministic score calculator with configurable weights and thresholds."""

    def __init__(self, weights: Optional[Dict[str, float]] = None,
                 thresholds: Optional[Dict[str, int]] = None):
        self.weights = weights or dict(DEFAULT_WEIGHTS)
        self.thresholds = thresholds or dict(DEFAULT_THRESHOLDS)

    def calculate(self, scores: ScoreInput) -> ScoreResult:
        """Calculate the weighted total score and determine decision."""
        weighted = {}
        total = 0.0
        clamped = {}

        for category, weight in self.weights.items():
            raw_score = getattr(scores, category, 50.0)
            # Clamp to 0-100
            clamped_score = max(0.0, min(100.0, raw_score))
            clamped[category] = round(clamped_score, 1)
            weighted_score = clamped_score * weight
            weighted[category] = round(weighted_score, 2)
            total += weighted_score

        total = round(total, 2)
        decision = self._get_decision(total)

        return ScoreResult(
            total=total,
            categories=clamped,
            weights=dict(self.weights),
            weighted_scores=weighted,
            decision=decision,
        )

    def _get_decision(self, total: float) -> str:
        """Determine decision based on total score and thresholds."""
        if total >= self.thresholds.get("bid", 75):
            return "bid"
        elif total >= self.thresholds.get("conditional_bid", 55):
            return "conditional_bid"
        else:
            return "skip"

    def to_dict(self, result: ScoreResult) -> Dict:
        """Serialize result to dict."""
        return {
            "total": result.total,
            "categories": result.categories,
            "weights": result.weights,
            "weighted_scores": result.weighted_scores,
            "decision": result.decision,
            "score_version": result.score_version,
            "thresholds": result.thresholds,
        }


# Test helper
def test_calculator() -> None:
    """Run basic tests on the score calculator."""
    calc = ScoreCalculator()

    # Test success scenario
    good = ScoreInput(
        technical_fit=90, proof_strength=85, client_quality=80,
        scope_clarity=75, budget_fit=70, competition_risk=80,
        delivery_confidence=85,
    )
    result = calc.calculate(good)
    assert result.total >= 75, f"Expected bid score >= 75, got {result.total}"
    assert result.decision == "bid", f"Expected 'bid', got '{result.decision}'"
    print(f"  Bid scenario: total={result.total}, decision={result.decision}")

    # Test conditional scenario
    conditional = ScoreInput(
        technical_fit=70, proof_strength=50, client_quality=65,
        scope_clarity=60, budget_fit=55, competition_risk=60,
        delivery_confidence=50,
    )
    result = calc.calculate(conditional)
    assert 55 <= result.total < 75, f"Expected conditional score 55-75, got {result.total}"
    assert result.decision == "conditional_bid", f"Expected 'conditional_bid', got '{result.decision}'"
    print(f"  Conditional scenario: total={result.total}, decision={result.decision}")

    # Test skip scenario
    skip = ScoreInput(
        technical_fit=30, proof_strength=20, client_quality=25,
        scope_clarity=40, budget_fit=35, competition_risk=50,
        delivery_confidence=20,
    )
    result = calc.calculate(skip)
    assert result.total < 55, f"Expected skip score < 55, got {result.total}"
    assert result.decision == "skip", f"Expected 'skip', got '{result.decision}'"
    print(f"  Skip scenario: total={result.total}, decision={result.decision}")

    # Test boundary
    boundary = ScoreInput(
        technical_fit=100, proof_strength=100, client_quality=100,
        scope_clarity=100, budget_fit=100, competition_risk=100,
        delivery_confidence=100,
    )
    result = calc.calculate(boundary)
    assert result.total == 100.0, f"Expected max 100, got {result.total}"
    print(f"  Max scenario: total={result.total}")

    # Test zero
    zero = ScoreInput(
        technical_fit=0, proof_strength=0, client_quality=0,
        scope_clarity=0, budget_fit=0, competition_risk=0,
        delivery_confidence=0,
    )
    result = calc.calculate(zero)
    assert result.total == 0.0, f"Expected min 0, got {result.total}"
    print(f"  Min scenario: total={result.total}")

    # Verify weights sum to 1.0
    total_weight = sum(DEFAULT_WEIGHTS.values())
    assert abs(total_weight - 1.0) < 0.001, f"Weights must sum to 1.0, got {total_weight}"
    print(f"  Weight sum: {total_weight}")

    print("\n  ✅ All scoring tests passed!")


if __name__ == "__main__":
    test_calculator()
