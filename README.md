# COSMOQUEST: Mission Survival — Version 7

An offline-first, responsive 2D science-learning game for children aged 7–12, written in HTML5, CSS3 and vanilla JavaScript. Available in **Russian (RU), English (EN) and Kazakh (ҚАЗ / KK)**. No npm, account, backend, real-money transactions or game server is required.

## Quick start

Double-click **`COSMOQUEST_single.html`** to play offline in Chrome, Edge or Firefox. It contains all required HTML, CSS, JavaScript, SVG artwork and learning data. For editing, use `index.html` with `styles.css` and `app.js` in the same folder. If a browser restricts local files, start a basic server in this directory with `python -m http.server 8000` and open `http://localhost:8000/`.

Player progress is stored locally via `localStorage`. The game intentionally does not collect a child's real name, email or address. To transfer progress between devices, choose **Settings → Export/Import JSON**.

## Version 7 — button and navigation audit

We reviewed all controls for meaningful behavior and fixed the following issues:

- **Concept glossary:** fixed three missing helper functions that could break the expanded "Details" dialog. It now shows contextual examples, related concepts, learning progress and direct lesson/review actions.
- **NASA Science:** opening a science-card heading now shows genuinely additional sections (how it works, connection to the game, scientific limitations), with a relevant activity button. NASA source links are still present; the removed "Learn" buttons have **not** returned.
- **Home MOXIE:** the button now goes directly to MOXIE's extended science detail instead of showing the same generic NASA card list.
- **Monster Shop:** "Compare" now shows the current and selected characters side-by-side. Unaffordable items explain the missing coins and provide an actual path to earn them, instead of a disabled purchase button.
- **Mission report:** "Full report" now includes a sol-by-sol decision history with net energy/oxygen/safety deltas and science rewards.
- **Daily concept task:** reviewing three distinct already-learned concepts now counts, so the goal remains attainable after completing all 36 lessons. The daily action takes a fully trained player to Scheduled Review.
- **Concept quiz:** a wrong answer now offers another attempt at the same concept instead of revealing the answer and allowing a skip.
- **Cosmic Recall:** explanations shown on demand do not remain automatically open for later questions.
- **Academy navigation:** clicking the main Academy navigation exits the current lesson to the Academy overview instead of leaving the user stranded in it.
- **Other small fixes:** nickname is retained when choosing a starter monster during onboarding; empty reset buttons in multi-step activities are disabled until there is something to clear.

The code continues to use the existing version-3 save schema and the same `localStorage` key, so previous in-browser progress can be restored automatically. Export a JSON backup before replacing a release.

### v7 checks

- `node --check app.js` — JavaScript syntax.
- `python test_v5.py` — **53 / 53** existing Academy, navigation, localization and responsive smoke checks passed.
- `python test_v7.py` — **23 / 23** new tests for meaningful buttons, popups, navigation, purchases, mission reports, daily learning, and explanations passed.
- `python test_persistence.py` — save recovery and no duplicate mini-game or daily rewards.
- `python build_v7.py && python test_standalone_v7.py` — standalone HTML tested at **360, 390, 768, 1024 and 1440 CSS px**, with zero JavaScript exceptions observed in those checks.
- All **71 generated action types** have registered action handlers (this is a static dispatch check, not proof of every possible dynamic state).

Tests cover specific scenarios, not every possible player action or operating system; browser `file://` behavior should be checked on the final demonstration machine.

## Version 5 changes — five-microstep Space Academy

Every one of the **36 science lessons** now follows the same five-step learning loop, in the currently selected language (RU, EN or KK):

1. **Discover in context:** a science concept, an illustrated three-node learning diagram, its definition, and a contextual sentence. No mandatory memorization before proceeding.
2. **Multiple choice:** choose the concept that matches its scientific definition. Correct and incorrect choices receive immediate visual feedback and optional synthesized audio.
3. **Match three pairs:** choose the correct concept for each of three definitions. An elapsed-time counter is shown when **Timed Challenges** is enabled; it disappears when the timer setting is off. Timer performance does not prevent children from progressing.
4. **Fill the gap:** type the concept into a meaningful space-science/engineering sentence in the selected interface language. Each concept has a tailored sentence for RU/EN/KK.
5. **Correct mistakes:** incorrectly answered choices, individual matching pairs and fill-in-the-gap prompts are repeated until corrected. Learners who made no errors proceed directly to completion.

The lesson displays a five-step progress bar, provides immediate success/error sounds when enabled, and now has a **Next / Далее / Келесі** button on the completion screen. From the sixth lesson in a module, this goes directly to the module's existing cumulative final challenge; otherwise it opens the next concept without returning to the learning map. Previously completed lessons do not pay their standard completion reward twice.

A **Scheduled Review / Повторение / Қайталау** tab was added. Completed concepts receive a simple spaced-review interval: **1, 3, 7, 14 or 30 days** after successive successful review sessions without errors; any errors reset the next review to tomorrow. Review dates (`words[id].due`), streak and mistakes are saved in the existing localStorage save. Legacy v2/v3 save records without scheduling fields are migrated to an initial 'due now' state, without losing coins, XP, achievements, lessons or monster purchases. This is intentionally a simple local scheduler, **not** an SM-2 implementation and not a push notification service.

### Suggested data structure for future lesson authoring

See **`academy_questions.json`** for a full, human-editable JSON representation of all **36 lessons**. Each entry keeps learning content apart from UI state:

```json
{
  "id": "w6",
  "moduleId": "spacecraft",
  "concept": {"ru": "Ракета", "en": "Rocket", "kk": "Зымыран"},
  "definition": {"ru": "Аппарат, движущийся благодаря выбросу газов.", "en": "A vehicle pushed by gases expelled at high speed.", "kk": "Газдарды жоғары жылдамдықпен шығару арқылы қозғалатын аппарат."},
  "visual": {"emoji": "🚀", "relatedConceptIds": ["w6", "w7", "w8"]},
  "microsteps": {
    "intro": {"context": {"ru": "{term} поднимает космический аппарат благодаря реактивной тяге.", "en": "A {term} launches a spacecraft using thrust.", "kk": "{term} реактивті күштің көмегімен ғарыш аппаратын ұшырады."}},
    "multipleChoice": {"correctId": "w6", "optionIds": ["w6", "w8", "w11"]},
    "matching": {"pairConceptIds": ["w6", "w8", "w10"]},
    "fillGap": {"sentence": {"ru": "____ поднимает космический аппарат благодаря реактивной тяге.", "en": "A ____ launches a spacecraft using thrust.", "kk": "____ реактивті күштің көмегімен ғарыш аппаратын ұшырады."}, "answerId": "w6"},
    "errorReview": {"repeatUntilCorrect": true}
  }
}
```

`academy_questions.json` is an editor-friendly export of the content currently embedded in `app.js`. The offline app **does not fetch this JSON** when starting. If you edit any `fillGap.sentence` values, run `python sync_gap_from_json.py` to update `app.js`, then rebuild the autonomous HTML by running `python build_v7.py`. To refresh the JSON's concepts and definitions after editing the existing `WORDS` bank in `app.js`, run `python build_academy_data.py`. This arrangement keeps the game functional when opened directly from a file, while providing a clear foundation for a future JSON-driven build pipeline.

## Version 5 verification

- `node --check app.js` — syntax valid.
- `python test_v5.py` — **53 end-to-end assertions passed** on the revised lesson flow and unaffected game screens (including all three languages, daily scheduler UI, module final, six mini-game launches, NASA links, the monster shop and five responsive widths).
- `python test_bundle_v5.py` — the **actual standalone HTML** runs when loaded into Chromium with its script at the end of the document; old version-3 saves are migrated, due concepts appear in Scheduled Review, and successful sessions advance review intervals from 1 to 3 days without duplicate lesson rewards.
- All **36 JSON entries** have a localized concept and definition, three multiple-choice options, three matching pairs, and one nonempty gap prompt in each language.
- Local HTTP and `file://` navigation are restricted in this test environment. The exact autonomous HTML was therefore tested using Chromium's `set_content` API. Direct file opening should still be checked on the actual demonstration machine.

## Version 4 changes — academy and NASA usability fixes

- **Monolingual Space Academy:** concept names, scientific definitions, lesson questions, answer choices, dictionary entries and flashcards appear **only in the selected app language** (Russian, English or Kazakh). The old translation and English fill-in-the-gap practice tabs have been removed. There is no longer a foreign-language learning requirement.
- **Six new final activities:** each of the six academy modules now contains **six concept lessons plus a seventh final matching task**. After completing all six lessons, players unlock a single combined activity that matches **all six definitions** with their concepts. An incorrect or incomplete submission is retryable. Completion is saved and the bonus is awarded only once. The combined activity can be replayed for practice without repeat rewards.
- **Moki/Orbit bug corrected:** an accidental replacement changed the English term `Orbit` into the mascot name `Moki` in one lesson. The scientific term is again `Orbit` (RU `Орбита`, KK `Орбита`). Moki remains only the helper monster.
- **NASA Science:** removed the **Explore / Изучить** button from each of the six cards and **kept their text, classification badges, icons, verified facts and NASA links unchanged**. Clicking the card title still opens the original detailed view, so the achievement tied to viewing science cards remains achievable.
- **Save compatibility:** the new `moduleFinals` field is added to the existing version-3 save format. Old version-2 and version-3 saves continue loading without loss of coins, monster purchases, mission progress or lessons. The save validator rejects inconsistent final-completion records.
- **Daily missions:** the academy task now refers to learning scientific concepts and their definitions, not learning another language.

## Version 3 changes

### Three-language localization

- **RU → EN → ҚАЗ** language button in the header, or choose the language in Settings.
- All main navigation items, missions, daily tasks, mini-game instructions, result screens, achievements, shop controls and settings have Kazakh translations.
- All **36 science concepts** have Russian, English and Kazakh names and definitions. The Academy displays only the currently selected language and can be searched in that language.
- Cosmic Recall accepts valid answers in Russian, English and Kazakh, including many alternative spellings. Scientific names and brand-like mini-game titles remain in their standard forms.
- The selected language is saved across sessions. Changing the language does not reset a running mission or the student's earned progress.

### Collectible space monsters

- Astronaut player avatars have been replaced by **10 unique, original SVG monster characters** with distinct outlines, eyes, colors and antennae/horns.
- **Bloop** and **Mossy** are available for free; the other **8 monsters** are purchased from the Monster Shop with earned Cosmo Coins.
- Each purchase is applied **once**, persists locally and unlocks a playable visual character. Players can switch between all unlocked monsters in the Monster Collection screen.
- Monsters are **cosmetic only**: owning one does not affect scientific scores, mission resources or learning progression.
- The helper character is **Moki**, a small space monster, replacing the earlier robot character.

### Expanded Cosmic Recall

- **37 question categories**, **268 groups of scientifically valid answers**, **797 accepted answer strings** across Russian, English, Kazakh and alternative forms.
- Questions include planetary science, moons, astronomy instruments, spacecraft technology, environmental hazards, missions, energy, physics and science careers.
- Each standard seven-question round selects a new mix of non-repeating questions. The daily seven-question set is based deterministically on the device's calendar date and is consistent throughout that day.
- Correct answers receive preset educational scores of 10, 20 or 30 points based on catalog position; these are **not actual player-frequency data**.
- Answers are normalized for capitalization, spacing, punctuation and `ё/е` spelling. A response does not require internet access or AI services.

## Main game modes

- **Mission Control:** a five-sol Mars habitat simulator with energy, oxygen and safety resources, forecasts, critical limits and consequences carried forward from the previous sol. Two difficulty settings change starting supplies.
- **Space Academy:** six modules, 36 five-step monolingual science lessons, six cumulative final challenges, a dictionary, flashcards, concept practice and spaced-review schedule.
- **Six mini-games:** Cosmic Recall, Cosmic Relay (one local player with scripted Moki or two to four players sharing one device), Power Master, Water Loop, Space Sort and Mission Fix.
- **Progress and economy:** XP, levels, twelve educational achievements, one-time mini-game prizes, daily missions, once-per-day challenge rewards, collectible monsters and saved settings.
- **Accessibility:** keyboard controls, large interactive targets, adjustable timers, reduced animations, high contrast and large text.

## Real NASA science versus simulation

The educational science cards use official references; their claims must not be confused with the simplified game model:

| Source | Science material | Status |
|---|---|---|
| [NASA Mars 2020 / MOXIE](https://science.nasa.gov/mission/mars-2020-perseverance/science-instruments/) | MOXIE produced 122 g of oxygen in total as a technology demonstration | Verified science material |
| [NASA ISS water recovery](https://www.nasa.gov/missions/station/iss-research/nasa-achieves-water-recovery-milestone-on-international-space-station/) | In 2023 a specific ISS system demonstrated up to 98% recovery of collected water | Verified science material |
| [NASA Space Communications](https://www.nasa.gov/missions/tech-demonstration/space-communications-7-things-you-need-to-know/) | Earth–Mars one-way communication delay of roughly 4–24 minutes | Verified science material |
| [NASA MEDA Jezero report](https://www.nasa.gov/directorates/stmd/nasas-first-weather-report-from-jezero-crater-on-mars/) | Selected published historical temperature observations | Historical record |
| [NASA OSDR OSD-37](https://osdr.nasa.gov/bio/repo/data/studies/OSD-37/) | Gene expression in four Arabidopsis thaliana ecotypes flown in space | Historical dataset |
| [NASA DONKI](https://api.nasa.gov/) | Optional recent CME event records retrieved on demand with `DEMO_KEY` | API records, if successfully retrieved |

Every numerical resource percentage, simulated warning or game score is **an educational game value**, not NASA telemetry, a forecast, or a radiation dose. A DONKI CME report alone cannot establish radiation conditions on Mars. The app works without the NASA API, and does not call it until the user chooses to load records.

## Saved progress and migration

The app recognizes the existing `cosmoquest-mission-survival-v2` localStorage key and transparently migrates **version 2** saves to **version 3**. Previously earned coins, XP, lessons, mission progress, achievements, daily records and the chosen language are preserved. The old astronaut cosmetic wardrobe has been replaced with the monster collection; migrating players start with the free Bloop monster while keeping their other game progression. Older cosmetic purchase identifiers are retained in the saved data for compatibility but are not sold or displayed as wearable monster equipment. Export a JSON backup before large changes or switching browsers.

Imported saves are size-checked and validated for their expected shape, allowed values and relevant state fields. Since the system is entirely client-side, it cannot prevent intentional modifications to local files or the device clock.

## Files and tests

```text
COSMOQUEST/
├── index.html                Multi-file entry point
├── styles.css                Responsive design and Academy styles
├── app.js                    Game logic, all localization, offline content
├── COSMOQUEST_single.html    Autonomous HTML game
├── academy_questions.json    36 full lesson entries (editor-friendly)
├── sync_gap_from_json.py     Embed edited gap prompts in app.js
├── build_academy_data.py     Export terms and localized prompts as JSON
├── test_v5.py               53 browser regression checks
├── test_bundle_v5.py        Autonomous HTML & legacy migration test
├── academy-preview-v5.png   Concept intro screenshot
├── academy-matching-v5.png  Matching screenshot
├── academy-review-v5.png    Error review screenshot
├── academy-next-v5.png      Next button on lesson completion
└── README.md                 Documentation
```

Legacy v4 tests and migration scripts may also remain in the development folder for historical reference, but several v4 tests assume the previous two-step lessons and are not the authoritative acceptance tests for v5.

## Known limits

- No online multiplayer or cloud synchronization; Cosmic Relay works locally with scripted Moki or players sharing one device.
- Child-friendly mission models are not a substitute for accurate engineering or atmospheric calculations.
- Language review by a native Kazakh-speaking educator is recommended before distribution to schools, especially for specialized scientific terms.
- The core app works offline; live DONKI retrieval is optional and can fail due to network restrictions, CORS or demo-key rate limits.
- This project is **not an official NASA application**. The mascot, game art and gameplay are original.
