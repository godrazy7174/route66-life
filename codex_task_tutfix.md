Fix tutorial text truncation and slightly raise beast pelt drops in this Overwatch 2 Workshop project by writing ONE Python patch script, patch102_tutfix.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints must be ASCII-safe (cp949 console): wrap non-ASCII prints in try/except or print ASCII labels only.

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~4,974 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions: `# -*- coding: utf-8 -*-`, Korean docstring, read file once, write once, assert everything you rely on. See patch101_mastery.py.
- Validation (run if possible): python patch102_tutfix.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Problem 1 - tutorial bodies truncate in game
Workshop Custom String literals are hard-capped at 128 characters at render time; several of the 18 tutorial page bodies exceed that and get cut mid-sentence in game (each literal's two-character `\r\n` escape sequence counts toward the cap as its 2 source characters - use source-character length as the metric).

The 18 tutorial body strings live inside ONE giant `Create HUD Text` line - the only line in the file containing `Min(17, Event Player.TutStep)` (it appears twice within that same line). The body array is the SECOND `Value In Array(Array(Custom String("..."), ...), Min(17, Event Player.TutStep))` expression on that line (the first array is the 18 short titles - leave titles untouched).

Fix programmatically (do not hand-enumerate the texts):
1. Locate that line (assert exactly one line contains `Min(17, Event Player.TutStep)`).
2. Parse the body array's 18 `Custom String("...")` literals (assert count == 18; bodies are distinguishable from titles because you take the second array).
3. For every body whose quoted content length (counting the literal backslash-r backslash-n sequences at their source length of 4 characters per newline... no - count PLAIN source characters of the quoted content as-is, where each `\r\n` escape pair is 4 source characters `\`,`r`,`\`,`n`; the in-game cost is 2 per newline, so to be safe use this rule:) compute L = number of source characters with each `\r\n` escape pair counted as 2. If L > 120, replace the literal `Custom String("BODY")` with `Custom String("{0}{1}", Custom String("PART1"), Custom String("PART2"))` where the split point is the `\r\n` boundary closest to the middle; PART1 keeps its trailing `\r\n` escape. Assert each resulting part has L <= 120. If a body has no newline or a part still exceeds 120, split at the space nearest the middle instead.
4. Do not alter any body's visible text - splitting only. Bodies with L <= 120 stay untouched.
5. After processing, assert the file still contains exactly one line with `Min(17, Event Player.TutStep)` and that no single `Custom String("...")` literal inside the body array has L > 120.

# Problem 2 - pelt drop bump (tiny)
Replace (cnt=1) `Set Player Variable(Attacker, Yield, Random Integer(1, 2));` with `Set Player Variable(Attacker, Yield, Random Integer(1, 3));` (base pelt roll 1-2 -> 1-3; all multipliers unchanged).

# Deliverables
patch102_tutfix.py (script alone suffices if the sandbox blocks execution). In your report: which of the 18 bodies (by index 0-17) were split, their before-lengths, and confirmation of the pelt change. Touch nothing else.
