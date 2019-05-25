#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
import re
import html

_wre = re.compile(r"\S+")

def _diff_words(s1, s2):
    # words1 = [util.escape(w.strip()) for w in words1.split(' ') if w.strip() != ""]
    # words2 = [w.strip() for w in words2.split(' ') if w.strip() != ""]
    words1 = re.findall(_wre, s1)
    words2 = re.findall(_wre, s2)

    # Timing: The basic Ratcliff-Obershelp algorithm is cubic time in the worst case and quadratic time in the expected case
    # https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher
    dr = difflib.Differ()
    diff = list(dr.compare(words1, words2))
    def dl2h(w):
        ww = w[2:]
        if   w.startswith('- '):  # disappeared
            return '<span class="diffminus modeldiffminus">%s</span>' % ww
        elif w.startswith('+ '):  # appeared
            return '<span class="diffplus modeldiffplus">%s</span>' % ww
        elif w.startswith('? '):  # not sure even what it means =)
            return ""
        elif w.startswith('  '):
            return ww
        else:
            return ww
    rw2 = map(dl2h, diff)
    return ' '.join(rw2)

def get_html(text1, text2):
    return _diff_words(text1, text2)
