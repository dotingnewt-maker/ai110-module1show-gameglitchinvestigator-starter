# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

---

## 1. What was broken when you started?

- **What did the game look like the first time you ran it?**  
  The first time I ran it I actually guessed correctly on the first try, but on closer inspection the difficulty settings were clearly off. Normal seemed much harder than Hard, which was the opposite of what I expected. The number of guesses allowed also seemed mismatched — Easy should give the most attempts, not Hard. The score feedback was confusing because it wasn't clear what actions raised or lowered it.

- **List at least two concrete bugs you noticed at the start:**
  1. **Hints were backwards** — when I guessed too high the game told me to go *higher*, and when I guessed too low it told me to go *lower*, which made it impossible to converge on the answer.
  2. **Hard mode was easier than Normal** — Hard used a range of 1–50 (narrower and therefore easier) while Normal used 1–100.
  3. **New Game didn't fully reset** — clicking New Game left the old score and status in place, so the "game over" message would persist from the previous round.
  4. **Attempt counter started at 1, not 0** — the game started counting from attempt #1 on first load, but New Game reset it to 0, so the counter was inconsistent between a fresh load and a restarted game.

---

## 2. How did you use AI as a teammate?

- **Which AI tools did you use?** Claude (via claude.ai).

- **One example of an AI suggestion that was CORRECT:**  
  I asked Claude to identify why the hint messages were wrong. It correctly spotted that `check_guess` returned `"📈 Go HIGHER!"` in the `if guess > secret` branch — exactly backwards. Claude suggested swapping the two return strings so that `guess > secret` maps to `"📉 Go LOWER!"` and `guess < secret` maps to `"📈 Go HIGHER!"`. I verified this by running `pytest tests/test_game_logic.py::TestCheckGuessHints`, which has five cases covering exact match, ±1 edge cases, and mid-range values — all passed after the swap. I also confirmed it in the live app by opening the Developer Debug Info panel (which shows the secret), guessing a number I knew was too high, and confirming the hint now said "Go LOWER."

- **One example of an AI suggestion that was INCORRECT or MISLEADING:**  
  When I asked about the `str` comparison issue (the original code cast `secret` to a string on even attempts before calling `check_guess`), Claude initially suggested making `check_guess` more "robust" by converting *both* values to strings inside the function: `if str(guess) == str(secret)`. That sounds safe, but it is actually wrong — Python compares strings lexicographically, so `"9" > "10"` is `True` because `"9"` comes after `"1"` alphabetically, even though 9 < 10 numerically. I caught this by running `>>> "9" > "10"` in a Python REPL and seeing `True`. The real fix was to remove the `str()` cast from `app.py` entirely and keep `check_guess` strictly integer, which I then verified with the `test_near_boundary_no_string_flip` test case.

---

## 3. Debugging and testing your fixes

- **How did I decide whether a bug was really fixed?**  
  I used two checks for every fix: a pytest case that targeted the exact broken behaviour, and a manual in-app test using the Developer Debug Info expander to see the secret. A fix wasn't "done" until both the test passed *and* the live game felt correct.

- **Describe at least one test and what it showed:**  
  `test_too_high_says_lower` in `TestCheckGuessHints` calls `check_guess(60, 50)` — a guess of 60 against a secret of 50 — and asserts that the outcome is `"Too High"` and that the string `"LOWER"` appears in the message. Before the fix this test failed because the message returned was `"📈 Go HIGHER!"`. After swapping the return values the test passed, confirming the hint now points the player in the right direction. A second useful test was `test_too_high_even_attempt_deducts` in `TestUpdateScore`, which called `update_score(100, "Too High", attempt_number=2)` and expected `95` — before the fix it returned `105` because the even-attempt branch added 5 instead of deducting.

- **Did AI help design or understand any tests?**  
  Yes. I asked Claude to suggest tests specifically targeting the bugs I had identified. It proposed the `test_near_boundary_no_string_flip` case (guessing 9 against secret 10) to catch the lexicographic comparison problem, which I would not have thought of on my own. I reviewed each suggested test to make sure the assertion logic matched the expected behaviour before including it.

---

## 4. What did you learn about Streamlit and state?

- **Why did the secret number keep changing in the original app?**  
  Streamlit re-runs the entire Python script from top to bottom every time a user clicks a button or changes an input. In the original code, `secret = random.randint(low, high)` was called as a plain variable (not inside `session_state`), so it was reassigned to a brand-new random number on every rerun — including every click of Submit.

- **How would you explain Streamlit reruns and session_state to a friend?**  
  Imagine every button click is like refreshing a webpage — the whole page reloads from scratch. `st.session_state` is like a sticky note attached to the browser tab: it survives the refresh. Any variable you store there at the start of a session (`if "secret" not in st.session_state`) is only created once; after that the rerun just reads the existing value instead of making a new one.

- **What change finally gave the game a stable secret?**  
  Wrapping the secret inside `if "secret" not in st.session_state: st.session_state.secret = random.randint(low, high)` meant the random number is generated exactly once per game session. Every subsequent rerun skips the `if` block and reads the same stored value, so the secret is stable from the player's first guess to their last.

---

## 5. Looking ahead: your developer habits

- **One habit I want to reuse in future projects:**  
  Writing a targeted pytest case *before* I consider a bug fixed. This lab showed me that "it looks right in the app" is not the same as "it is actually correct." The `test_near_boundary_no_string_flip` case caught a subtle lexicographic comparison bug that would have been very hard to spot just by playing the game. I will write at least one test per bug fix going forward.

- **One thing I would do differently next time:**  
  I would ask the AI to *explain* its suggestion before I accepted it, not just paste in the code. The misleading `str()` suggestion looked plausible on the surface, and I almost used it. If I had asked "why does this work?" first, I would have caught the lexicographic ordering problem immediately instead of discovering it through a REPL experiment afterward.

- **How this project changed the way I think about AI-generated code:**  
  AI can write plausible-looking code that is subtly wrong in ways that only show up under specific inputs — like the string comparison that fails only for two-digit numbers starting with 1. I now treat AI-generated code the way I would treat code from a confident but fallible colleague: read it carefully, understand it, and test it before trusting it.