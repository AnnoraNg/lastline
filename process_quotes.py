"""
Parse 8000animequotes.csv and produce quotes_{short,medium,long}.js with
filtering for inappropriate / nonsensical quotes.

Run from the project folder:
    python3 process_quotes.py

To re-run after updating the CSV: same command. The three .js files are
overwritten in place.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "8000animequotes.csv")
OUT_DIR = HERE

SHORT_MAX = 80      # inclusive upper bound for short
MEDIUM_MAX = 200    # inclusive upper bound for medium
LONG_MAX = 500      # cap on long — anything longer is unwieldy
MIN_LEN = 10        # toss anything shorter than 10 chars after cleaning
MIN_WORDS = 3       # toss interjections/fragments

# ----------------------------------------------------------------------------
# Filter lists
# ----------------------------------------------------------------------------

# Hard blocklist: any quote containing one of these words (with word boundaries
# applied) is dropped. Conservative: includes profanity, slurs, sexual terms.
PROFANITY = {
    # sexual
    "sex", "sexy", "sexual", "horny", "porn", "porno", "hentai", "ecchi",
    "boobs", "boob", "tits", "tit", "breasts", "nipple", "nipples",
    "panties", "panty", "lingerie",
    "pussy", "pussies", "cunt", "cunts",
    "cock", "cocks", "dick", "dicks",
    "fuck", "fucking", "fucked", "fucker", "fuckers", "fck", "fking",
    "motherfucker", "mf",
    "ballsack", "balls", "ballsacks",
    "blowjob", "handjob", "rimjob",
    "cum", "cumming", "cummed",
    # slurs
    "nigga", "niggas", "nigger", "niggers",
    "fag", "faggot", "faggots",
    "retard", "retarded", "retards",
    "tranny", "trannies",
    # gendered/derogatory
    "slut", "sluts", "slutty", "whore", "whores", "whoring",
    "bitch", "bitches", "bitching", "bitchy",
    "bastard", "bastards",
    # violence-as-content (keeping general "kill"/"die"/"blood" — those are core
    # anime vocabulary; only filtering specifically sexual-violence terms)
    "rape", "raped", "rapes", "rapist", "rapists", "raping",
    "molest", "molested", "molesting", "molester",
    "incest",
    "pedo", "pedophile", "pedophilia", "loli", "shota",
    # scatological/coarse
    "shit", "shitty", "shitter", "shitting", "shits", "bullshit",
    "asshole", "assholes", "asshat", "asshats",
    # body parts in vulgar context
    "anal", "anus",
    "vagina", "vaginas", "penis", "penises",
}

# Sound-effect / interjection words. A quote whose word list is >40% these
# is dropped (these are usually transcribed grunts, not lines).
SOUND_FX = {
    "ah", "aha", "ahh", "ahhh", "ahhhh", "aha", "ahaha",
    "argh", "arghh", "arghhh",
    "eh", "ehh", "ehhh", "ehhhh", "ehe", "ehehe",
    "uh", "uhh", "uhhh", "uhuh",
    "um", "umm", "ummm",
    "huh",
    "hmm", "hmmm", "hmmmm",
    "ha", "haha", "hahaha", "hahahaha",
    "he", "hehe", "hehehe",
    "ho", "hoho", "hohoho",
    "wah", "wahh", "waah", "waaah", "waaaah",
    "whoa", "woah", "wow", "yay",
    "ow", "owch", "ouch", "oof",
    "ne", "ja", "ano", "etto",  # untranslated japanese fillers
    "sou", "souka", "yare",
    "tch",
    "oh", "ohh", "ohhh", "ohhhh",
    "yo",
    "mm", "mmm", "mmhmm",
    "ya",
    "psh", "pft", "pfft",
}

# Words that often signal a quote was transcribed mid-sentence — ending on these
# means the line is a fragment.
TRAILING_FRAGMENT_WORDS = {
    "and", "or", "but", "so", "if", "because", "since", "though", "although",
    "while", "however", "therefore", "thus", "the", "a", "an", "of", "to",
    "with", "for", "from", "by", "in", "on", "at", "is", "was", "are", "were",
    "that", "which", "who", "whom", "whose",
}

# Words that hint at meta/self-referential commentary, not in-fiction dialogue.
META_WORDS = {
    "anime", "manga", "episode", "season", "filler", "fanservice",
    "weeb", "weeaboo", "otaku",
}

# ----------------------------------------------------------------------------
# Cleaning
# ----------------------------------------------------------------------------

def clean_quote(text: str) -> str:
    """Lowercase, strip apostrophes, normalise punctuation/whitespace.
    Output contains only [a-z 0-9] + single spaces."""
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r"[’‘']", "", t)               # strip apostrophes
    t = re.sub(r"[—–‒/\\\-]", " ", t)         # dashes/slashes -> space
    t = re.sub(r"[…]", " ", t)                # ellipses -> space
    t = re.sub(r"[^a-z0-9 ]", " ", t)         # everything else
    t = re.sub(r"\s+", " ", t).strip()
    return t

def clean_anime(text: str) -> str:
    if not text:
        return ""
    return text.strip().strip("()").strip()

def clean_character(text: str) -> str:
    return text.strip() if text else ""

def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

# ----------------------------------------------------------------------------
# Filtering
# ----------------------------------------------------------------------------

def reject_reason(quote: str):
    """Return None if the quote is acceptable, else a short string explaining why."""
    words = quote.split()
    n = len(words)
    if n < MIN_WORDS:
        return "too_few_words"
    word_set = set(words)
    # Profanity / slurs
    bad = word_set & PROFANITY
    if bad:
        return f"profanity:{next(iter(bad))}"
    # Meta self-references
    if word_set & META_WORDS:
        return "meta"
    # All-numeric or mostly numeric
    if all(w.isdigit() for w in words):
        return "all_numeric"
    # Sound effects / interjections dominate
    fx_count = sum(1 for w in words if w in SOUND_FX)
    if fx_count / n > 0.4:
        return "sound_effects"
    # Repetition: same word 3+ times in a row
    for i in range(n - 2):
        if words[i] == words[i+1] == words[i+2]:
            return "triple_repeat"
    # Low uniqueness ratio for longer quotes
    if n >= 8 and len(word_set) / n < 0.5:
        return "low_uniqueness"
    # Fragment indicators: ends on conjunction/preposition/article (translation cut)
    if words[-1] in TRAILING_FRAGMENT_WORDS:
        return "trailing_fragment"
    # Starts with a conjunction-only fragment (rare but happens)
    if n >= 6 and words[0] in {"and", "or", "but"} and words[1] in {"and", "or", "but"}:
        return "leading_fragment"
    return None

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def category_for(quote: str):
    n = len(quote)
    if n < MIN_LEN: return "skip_short"
    if n > LONG_MAX: return "skip_long"
    if n <= SHORT_MAX: return "short"
    if n <= MEDIUM_MAX: return "medium"
    return "long"

def main():
    pools = {"short": [], "medium": [], "long": []}
    seen = {"short": set(), "medium": set(), "long": set()}
    counters = {
        "total": 0,
        "duplicate": 0,
        "out_of_bounds": 0,
        "missing_field": 0,
    }
    reject_counts = {}
    sampled_rejects = []  # (reason, quote) — first 30 of each reason

    with open(CSV_PATH, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader, None)  # header
        for row in reader:
            counters["total"] += 1
            if len(row) < 4:
                counters["missing_field"] += 1
                continue
            anime = clean_anime(row[1])
            character = clean_character(row[2])
            quote = clean_quote(row[3])
            if not quote or not anime:
                counters["missing_field"] += 1
                continue
            cat = category_for(quote)
            if cat.startswith("skip"):
                counters["out_of_bounds"] += 1
                continue
            reason = reject_reason(quote)
            if reason is not None:
                reject_counts[reason] = reject_counts.get(reason, 0) + 1
                if len(sampled_rejects) < 200 and reason.startswith("profanity"):
                    sampled_rejects.append((reason, quote))
                continue
            if quote in seen[cat]:
                counters["duplicate"] += 1
                continue
            seen[cat].add(quote)
            if character and character.lower() != anime.lower():
                source = f"{character} · {anime}"
            else:
                source = anime
            pools[cat].append((quote, source))

    # Write the three JS files
    blurbs = {
        "short": "Each entry must be ≤ 80 characters (one-liners, punchy quotes).",
        "medium": "Each entry is roughly 80 to 200 characters (a sentence or two).",
        "long": "Each entry is 200 to 500 characters (stamina runs).",
    }
    for cat in ("short", "medium", "long"):
        path = os.path.join(OUT_DIR, f"quotes_{cat}.js")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"""// ============================================================================
// Last Line — {cat} quotes
// ============================================================================
// Auto-generated from 8000animequotes.csv. {len(pools[cat])} entries.
//
// Format per entry: {{ t: "the quote text", s: "Character · Series" }}
//   • t = lowercase plain text, only [a-z 0-9 space]. Apostrophes have been
//         stripped (don't -> dont, i'm -> im). No commas, periods, em-dashes.
//   • s = "Character · Series". The middle dot is the · character.
//         When the source has no distinct character, just the series name is used.
//
// Length rule: {blurbs[cat]}
//   short  ≤ 80 chars       (quotes_short.js)
//   medium 80 to 200 chars  (quotes_medium.js)
//   long   200 to 500 chars (quotes_long.js)
//
// To add a new quote by hand: append a new {{...}} object to the array below.
// Trailing comma after every entry is fine. Save, refresh the game.
// ============================================================================

window.QUOTES = window.QUOTES || {{}};
window.QUOTES.{cat} = [
""")
            for q, s in pools[cat]:
                f.write(f'  {{ t: "{js_escape(q)}", s: "{js_escape(s)}" }},\n')
            f.write("];\n")

    # Report
    print(f"Total CSV rows scanned: {counters['total']}")
    print(f"  Missing fields:        {counters['missing_field']}")
    print(f"  Out of bounds:         {counters['out_of_bounds']}")
    print(f"  Duplicates after clean:{counters['duplicate']}")
    total_rejected = sum(reject_counts.values())
    print(f"  Filter rejects:        {total_rejected}")
    if reject_counts:
        for reason, count in sorted(reject_counts.items(), key=lambda x: -x[1]):
            print(f"    {reason:<25} {count}")
    print()
    print(f"Kept: short={len(pools['short'])}  medium={len(pools['medium'])}  long={len(pools['long'])}")
    print(f"Total kept: {sum(len(p) for p in pools.values())}")

if __name__ == "__main__":
    main()
