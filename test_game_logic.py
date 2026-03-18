"""
test_game_logic.py

Pytest suite for the bugs fixed in logic_utils.py.

Primary targets:
  1. check_guess — reversed hint messages
  2. check_guess — str/int type coercion removed (always int now)
  3. update_score — even-attempt "Too High" reward removed
  4. get_range_for_difficulty — Hard wider than Normal
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logic_utils import (
    check_guess,
    parse_guess,
    update_score,
    get_range_for_difficulty,
)


# ── Bug 1 fix: hint messages point the correct direction ─────────────────────

class TestCheckGuessHints:

    def test_too_high_says_lower(self):
        """Guessing above the secret should tell the player to go LOWER."""
        outcome, message = check_guess(60, 50)
        assert outcome == "Too High"
        assert "LOWER" in message, f"Expected LOWER, got: {message!r}"

    def test_too_low_says_higher(self):
        """Guessing below the secret should tell the player to go HIGHER."""
        outcome, message = check_guess(30, 50)
        assert outcome == "Too Low"
        assert "HIGHER" in message, f"Expected HIGHER, got: {message!r}"

    def test_correct_guess_wins(self):
        outcome, message = check_guess(42, 42)
        assert outcome == "Win"
        assert "Correct" in message

    def test_one_above_secret(self):
        outcome, message = check_guess(51, 50)
        assert outcome == "Too High"
        assert "LOWER" in message

    def test_one_below_secret(self):
        outcome, message = check_guess(49, 50)
        assert outcome == "Too Low"
        assert "HIGHER" in message


# ── Bug 2 fix: int-only comparison (no str coercion) ────────────────────────

class TestCheckGuessTypes:

    def test_int_win(self):
        outcome, _ = check_guess(7, 7)
        assert outcome == "Win"

    def test_int_too_high(self):
        outcome, _ = check_guess(10, 5)
        assert outcome == "Too High"

    def test_int_too_low(self):
        outcome, _ = check_guess(3, 5)
        assert outcome == "Too Low"

    def test_near_boundary_no_string_flip(self):
        # str comparison: "9" > "10" is True in Python — numeric must be False.
        outcome, message = check_guess(9, 10)
        assert outcome == "Too Low"
        assert "HIGHER" in message

    def test_hard_mode_large_numbers(self):
        outcome, message = check_guess(199, 200)
        assert outcome == "Too Low"
        assert "HIGHER" in message


# ── Bug 3 fix: update_score never rewards wrong guesses ─────────────────────

class TestUpdateScore:

    def test_too_high_even_attempt_deducts(self):
        """Even-attempt Too High used to give +5; should now be -5."""
        result = update_score(100, "Too High", attempt_number=2)
        assert result == 95, f"Expected 95, got {result}"

    def test_too_high_odd_attempt_deducts(self):
        result = update_score(100, "Too High", attempt_number=3)
        assert result == 95

    def test_too_low_deducts(self):
        result = update_score(100, "Too Low", attempt_number=1)
        assert result == 95

    def test_win_adds_points(self):
        result = update_score(0, "Win", attempt_number=1)
        assert result > 0

    def test_win_floor_is_10(self):
        """Very late wins still award at least 10 points."""
        result = update_score(0, "Win", attempt_number=20)
        assert result == 10


# ── Bug 4 fix: Hard range wider than Normal ──────────────────────────────────

class TestDifficultyRanges:

    def test_hard_wider_than_normal(self):
        _, normal_high = get_range_for_difficulty("Normal")
        _, hard_high   = get_range_for_difficulty("Hard")
        assert hard_high > normal_high, (
            f"Hard upper bound ({hard_high}) should exceed Normal ({normal_high})"
        )

    def test_easy_narrower_than_normal(self):
        _, easy_high   = get_range_for_difficulty("Easy")
        _, normal_high = get_range_for_difficulty("Normal")
        assert easy_high < normal_high

    def test_unknown_difficulty_defaults(self):
        low, high = get_range_for_difficulty("Impossible")
        assert low == 1 and high == 100


# ── parse_guess sanity checks ────────────────────────────────────────────────

class TestParseGuess:

    def test_valid_int(self):
        ok, val, err = parse_guess("42")
        assert ok and val == 42 and err is None

    def test_float_truncates(self):
        ok, val, _ = parse_guess("7.9")
        assert ok and val == 7

    def test_empty(self):
        ok, val, err = parse_guess("")
        assert not ok and val is None

    def test_none(self):
        ok, _, _ = parse_guess(None)
        assert not ok

    def test_non_numeric(self):
        ok, _, err = parse_guess("banana")
        assert not ok and "not a number" in err.lower()