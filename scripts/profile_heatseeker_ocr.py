#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/heatseeker_observed_2026-08-24/heatseeker_observed.jsonl')
OUTDIR = SOURCE.parent

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{1,31}")
TIMEISH_RE = re.compile(r"\b(?:[01]?\d|2[0-3])[:.]\d{2}(?::\d{2})?\b")

# Generic UI / chart words suppressed only for frequency ranking. Raw OCR is untouched.
NOISE = {
    'the','and','for','with','from','this','that','your','you','are','not','all','new','now',
    'open','close','high','low','volume','price','chart','data','time','date','call','put',
    'calls','puts','option','options','market','markets','am','pm','usd','day','days','week',
    'weeks','month','months','year','years','share','image','img','screenshot','http','https',
}


def norm_word(token: str) -> str:
    return token.strip('_-').lower()


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f'missing OCR dataset: {SOURCE}')

    rows=[]
    for line in SOURCE.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(json.loads(line))

    token_counts=Counter()
    token_images=defaultdict(set)
    line_counts=Counter()
    line_images=defaultdict(set)

    for idx,row in enumerate(rows,1):
        for raw in row.get('raw_text',[]):
            text=' '.join(str(raw).split())
            if not text:
                continue
            line_counts[text]+=1
            line_images[text].add(idx)
            for token in WORD_RE.findall(text):
                word=norm_word(token)
                if len(word)<2 or word in NOISE:
                    continue
                token_counts[word]+=1
                token_images[word].add(idx)

    # Rank by number of different images first, then total OCR occurrences.
    ranked_tokens=sorted(
        token_counts,
        key=lambda w:(len(token_images[w]), token_counts[w], w),
        reverse=True,
    )
    ranked_lines=sorted(
        line_counts,
        key=lambda s:(len(line_images[s]), line_counts[s], s),
        reverse=True,
    )

    report={
        'images':len(rows),
        'top_tokens':[
            {'token':w,'images':len(token_images[w]),'occurrences':token_counts[w]}
            for w in ranked_tokens[:80]
        ],
        'repeated_lines':[
            {'text':s,'images':len(line_images[s]),'occurrences':line_counts[s]}
            for s in ranked_lines if len(line_images[s])>=2
        ][:50],
        'per_image':[],
    }

    print('\n=== OCR VOCABULARY: TOP TOKENS ===')
    for item in report['top_tokens'][:50]:
        print(f"{item['token']:<24} images={item['images']:>2} occurrences={item['occurrences']:>3}")

    print('\n=== REPEATED OCR LINES ===')
    for item in report['repeated_lines'][:25]:
        print(f"images={item['images']:>2} occurrences={item['occurrences']:>3} | {item['text']}")

    print('\n=== PER IMAGE CANDIDATES ===')
    for idx,row in enumerate(rows,1):
        raw_text=[str(x) for x in row.get('raw_text',[])]
        timeish=[]
        for text in raw_text:
            timeish.extend(TIMEISH_RE.findall(text))
        timeish=list(dict.fromkeys(timeish))
        item={
            'index':idx,
            'basename':row.get('basename',''),
            'filename_time_naive':row.get('filename_time_naive',''),
            'visible_time_candidates':row.get('visible_time_candidates',[]),
            'timeish_ocr_tokens':timeish,
            'ticker_candidates':row.get('ticker_candidates',[]),
            'raw_text_preview':raw_text[:12],
        }
        report['per_image'].append(item)
        print(f"{idx:02d} {item['basename']}")
        print(f"   filename_time={item['filename_time_naive'] or '-'} visible_time={item['visible_time_candidates'] or '-'} ticker={item['ticker_candidates'] or '-'}")
        preview=' | '.join(item['raw_text_preview'][:6])
        print(f"   OCR: {preview}")

    out=OUTDIR/'ocr_profile.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'\n[OpenClaw] profile written: {out}')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
