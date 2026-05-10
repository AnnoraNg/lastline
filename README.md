# Last Line

A side-scrolling anime typing game. Type real anime quotes to outrun the monster or get eaten.

## About

Keyboard-only browser game. The player runs from left to right while a monster chases from behind. Typing quotes correctly pushes the player forward and knocks the monster back; mistakes let it gain ground. Survive ten stages of increasing monster speed across themed biomes — plains, forest, desert, caves, volcano, tundra, peaks, ruins, abyss, void.

- **3 difficulty modes**: Easy, Medium, Hard, with score multipliers ×1 / ×2 / ×3
- **3 quote-length modes**: short, medium, long
- **~7,900 real anime quotes** across 700+ series
- **Series filter** to play only your favorite anime (e.g. Naruto only, Bleach only)
- **Local leaderboard** per difficulty, persisted in your browser

## How to play

| Action | Key |
|---|---|
| Type the quote | letter and space keys |
| Skip the current word | `Tab` |
| Restart | `Restart` button |
| View the leaderboard | `Leaderboard` button |

Stop typing for 7 seconds and the monster surges. If it catches you, the run ends. After the run you can save your score with a name and watch yourself climb (or fall off) the leaderboard.

## Stages

Numbers are the monster's typing speed in WPM. Stages 5+ get challenging quickly; stages 8+ are tournament-pro tier.

| # | Stage | Easy | Medium | Hard |
|---|---|---:|---:|---:|
| 1 | plains | 40 | 60 | 90 |
| 2 | forest | 55 | 75 | 110 |
| 3 | desert | 70 | 90 | 130 |
| 4 | caves | 85 | 110 | 155 |
| 5 | volcano | 105 | 135 | 185 |
| 6 | tundra | 125 | 160 | 215 |
| 7 | peaks | 145 | 185 | 250 |
| 8 | ruins | 170 | 215 | 285 |
| 9 | abyss | 200 | 245 | 320 |
| 10 | void | 230 | 280 | 360 |

## Run it locally

It's a single static HTML file with three sibling JS files for the quote pool. No build step, no server, no dependencies.

Download the four files (`index.html`, `quotes_short.js`, `quotes_medium.js`, `quotes_long.js`) and double-click `index.html`. Any modern browser works (Chrome, Safari, Firefox, Edge).

## Tech notes

- Vanilla HTML, CSS, and JavaScript — no frameworks, no bundler, no build tools
- All visuals (player, monster, scenery) are inline SVG drawn procedurally
- Quote pool loaded from sibling `quotes_*.js` files via plain `<script src>` tags
- Leaderboard persisted via `localStorage`, scoped per browser

## File layout

```
index.html              Game (HTML + CSS + JavaScript, all inline)
quotes_short.js         Short quotes (≤ 80 chars)
quotes_medium.js        Medium quotes (80–200 chars)
quotes_long.js          Long quotes (200+ chars)
process_quotes.py       Build script — regenerates the JS pools from the CSV
8000animequotes.csv     Source dataset
```

## Credits

Quote data sourced from a public anime-quotes dataset, with curated additions from a few public anime-quote roundups. All in-game visuals are SVG drawn procedurally.
