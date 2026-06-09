#!/usr/bin/env python3
"""Structural assertions over generated workshop output. Exit non-zero on failure."""
import os, sys, json
ROOT = os.path.join(os.path.dirname(__file__), "..")
content = json.load(open(os.path.join(ROOT, "data", "workshops_content.json"), encoding="utf-8"))

def check():
    idx = os.path.join(ROOT, "workshops", "index.html")
    assert os.path.exists(idx), "missing workshops/index.html"
    home = open(idx, encoding="utf-8").read()
    assert home.count('class="mod-card') == 7, "landing must show 7 category cards"
    for slug in content:
        p = os.path.join(ROOT, "workshops", slug + ".html")
        assert os.path.exists(p), f"missing page {slug}"
        h = open(p, encoding="utf-8").read()
        for need in ('class="glance"', 'id="quiz"', 'data-mod=', 'app.css'):
            assert need in h, f"{slug} missing {need}"
        assert "var(--p)" not in h and "var(--teal)" not in h, f"{slug} has legacy tokens"
        assert 'id="pt"' not in h, f"{slug} still uses non-unique id=pt for prompt"
    print(f"OK: index + {len(content)} workshop pages pass structural checks")

if __name__ == "__main__":
    try:
        check()
    except AssertionError as e:
        print("FAIL:", e); sys.exit(1)
