# COSMOQUEST v7 — Interactive Control Audit

| Area | Previously weak behavior | v7 result |
|---|---|---|
| Glossary Details | Could error due to missing functions | Fixed functions; context, related terms, progress and lesson navigation work |
| NASA science titles | Modal repeated the card | New method, game link and limitations; original NASA link retained |
| Home MOXIE link | Opened generic listing | Opens MOXIE detail directly |
| Monster Shop Preview | Enlarged identical character view | Compares current and candidate; buy or earn coins |
| Insufficient coins | Disabled buy with no explanation | Shows the shortfall and an earn-coins action |
| Full Mission Report | Repeated final resource summary | Lists each sol, choice, net resource change and science score |
| Daily learning button | Ended at generic academy and became infeasible when 36 words learned | Goes to review when appropriate; distinct repeat sessions count |
| Vocabulary practice Next | Incorrect answer could be skipped | Retry same question until correct |
| Recall Show explanation | Enabled reveal for later questions | Per-question reset |
| Academy main navigation | Could remain inside prior lesson | Exits to academy overview |
| Onboarding monster choice | Could wipe typed nickname | Preserves nickname |
| Clear answers / Clear sequence | Looked clickable with nothing to clear | Disabled when empty |

## Verification

- All 71 distinct rendered `data-action` types map to a registered handler.
- 53 legacy browser assertions passed (`test_v5.py`).
- 23 specific v7 browser assertions passed (`test_v7.py`).
- Standalone HTML verified at 360, 390, 768, 1024, and 1440 px (`test_standalone_v7.py`).
- Save restore and non-duplicated rewards checked (`test_persistence.py`).

This audit is not a formal proof that every possible player path is free of errors; only the specific conditions above were tested. The game runs fully offline, while an optional NASA DONKI request still needs network access.
