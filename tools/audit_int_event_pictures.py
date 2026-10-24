"""Inventory visible interwar event pictures for Germany and both Russias."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVENT_DIR = ROOT / "events"
EVENT_START = re.compile(r"(?m)^(country_event|news_event)\s*=\s*\{")
FIELD = lambda key: re.compile(rf"(?m)^\s*{key}\s*=\s*([^\s#]+)")


def english_titles() -> dict[str, str]:
    names = {}
    pattern = re.compile(r'^\s*([^#:\s]+):\d*\s+"(.*)"')
    for path in (ROOT / "localisation").rglob("*l_english.yml"):
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = pattern.match(line)
            if match:
                names[match.group(1)] = match.group(2)
    return names


def events() -> list[dict[str, str]]:
    result = []
    titles = english_titles()
    for path in sorted(EVENT_DIR.glob("INT*")):
        script = path.read_text(encoding="utf-8-sig")
        starts = list(EVENT_START.finditer(script))
        for index, start in enumerate(starts):
            block = script[start.end():starts[index + 1].start() if index + 1 < len(starts) else len(script)]
            identifier = FIELD("id").search(block)
            if not identifier:
                continue
            hidden = FIELD("hidden").search(block)
            if hidden and hidden.group(1) == "yes":
                continue
            title = FIELD("title").search(block)
            picture = FIELD("picture").search(block)
            title_key = title.group(1) if title else ""
            result.append({"id": identifier.group(1), "kind": start.group(1),
                           "title": title_key, "label": titles.get(title_key, title_key),
                           "picture": picture.group(1) if picture else "",
                           "file": path.name})
    return result


if __name__ == "__main__":
    records = events()
    for record in records:
        print("|".join(record[key] for key in ("id", "kind", "label", "picture", "file")))
    print(f"VISIBLE={len(records)} UNIQUE_PICTURE_KEYS={len({row['picture'] for row in records})}")
    counts = Counter(row["picture"] for row in records)
    for picture, count in counts.most_common():
        if count > 1:
            print(f"DUPLICATE={count} {picture}")
