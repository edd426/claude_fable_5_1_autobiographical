#!/usr/bin/env python3
"""Check that index.html says what fable.1 says.

Renders fable.1 with mandoc, strips index.html to its text, normalizes both,
and reports the first place they differ. Exit 0 when they agree.
"""
import difflib
import html
import re
import subprocess
import sys

def norm(t):
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("‐", "-").replace("‑", "-")
    return re.sub(r"\s+", " ", t).strip().lower()

def man_text():
    out = subprocess.run(["mandoc", "-T", "utf8", "fable.1"], capture_output=True, text=True, check=True).stdout
    out = re.sub(r".\x08", "", out)           # drop overstrike bold/underline
    out = re.sub(r"-\n\s*", "-", out)          # rejoin words mandoc broke at a hyphen
    return norm(out)

def html_text():
    s = open("index.html", encoding="utf-8").read()
    s = re.search(r"<main.*?</main>", s, re.S).group(0)
    s = re.sub(r"</?(b|i|a)\b[^>]*>", "", s)   # inline tags: no space
    s = re.sub(r"<[^>]+>", " ", s)                    # block tags: a space
    return norm(html.unescape(s))

a, b = man_text(), html_text()
if a == b:
    print("ok: index.html matches fable.1 (%d characters)" % len(a))
    sys.exit(0)
aw, bw = a.split(" "), b.split(" ")
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, aw, bw).get_opcodes():
    if op != "equal":
        print("%s\n  man:  %s\n  html: %s" % (op, " ".join(aw[max(0,i1-4):i2+4]), " ".join(bw[max(0,j1-4):j2+4])))
sys.exit(1)
