#!/usr/bin/env python3
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding='utf-8') if len(sys.argv) > 1 else sys.stdin.read()

checks = {
    'has_dialogue': '“' in text or '"' in text,
    'has_hook_like_end': len(text.strip().splitlines()) > 0 and text.strip()[-1] in '！？?!。',
    'paragraph_count_ge_8': len([p for p in text.splitlines() if p.strip()]) >= 8,
    'not_too_many_fillers': sum(text.count(x) for x in ['与此同时','然而','显然','事情并没有那么简单']) <= 6,
}

failed = [k for k, v in checks.items() if not v]
if failed:
    print('WARN')
    for item in failed:
        print(item)
else:
    print('OK')
