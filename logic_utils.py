"""
logic_utils.py
Core game logic refactored from app.py.

Bugs fixed in this file:
  - check_guess: hint messages were reversed (HIGHER when too high, LOWER when too low).
    FIX: messages now point the player in the correct direction.
  - update_score: rewarded +5 on even-numbered "Too High" guesses (wrong is wrong).
    FIX: always deduct 5 for any incorrect guess.
  - get_range_for_difficulty: Hard returned (1, 50), narrower than Normal (1, 100).
    FIX: Hard now returns (1, 200).
"""


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        # FIXME: original returned (1, 50) which is easier than Normal's (1, 100).
        # FIX: widened to (1, 200) so Hard is genuinely harder than Normal.
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an integer guess.
    Returns (ok: bool, guess_int: int | None, error_message: str | None).
    """
    if raw is None:
        return False, None, "Enter a guess."
    if raw == "":
        return False, None, "Enter a guess."
    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."
    return True, value, None


def check_guess(guess: int, secret: int):
    """
    Compare guess to secret and return (outcome, message).

    FIXME (original): messages were reversed —
      guess > secret fired "📈 Go HIGHER!" (told player to go the wrong way)
      guess < secret fired "📉 Go LOWER!" (also wrong)
    FIX: messages now correctly tell the player which direction to move next.
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        # Player guessed above the secret → next guess should be lower.
        # FIX: was "📈 Go HIGHER!" — corrected to "📉 Go LOWER!"
        return "Too High", "📉 Go LOWER!"
    else:
        # Player guessed below the secret → next guess should be higher.
        # FIX: was "📉 Go LOWER!" — corrected to "📈 Go HIGHER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Update score based on outcome and attempt number.

    FIXME (original): on even attempts, "Too High" returned current_score + 5,
    rewarding the player for a wrong guess every other turn.
    FIX: all wrong guesses always deduct 5.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        # FIX: removed the even-attempt +5 reward branch.
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score