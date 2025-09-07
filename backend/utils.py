# backend/utils.py
import re


def clean_text(s: str) -> str:
    # basic cleaning
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def format_sources_for_display(sources):
    out = []
    for i, meta in enumerate(sources):
        snippet = meta.get('text', '') if isinstance(meta, dict) else str(meta)
        out.append(f"Source {i+1}: {snippet[:200]}")
    return "\n".join(out)
