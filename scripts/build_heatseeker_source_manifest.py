#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/BUREAU_MAC')
OUT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata')
EXTS = {'.png','.jpg','.jpeg','.webp'}
DATE_RE = re.compile(r'(20\d{2}-\d{2}-\d{2})')
SHOT_RE = re.compile(r'(20\d{2}-\d{2}-\d{2})[_ ]at[_ ](\d{1,2})[._](\d{2})[._](\d{2})[_ ](AM|PM)', re.I)

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def filename_ts(name:str)->str:
    m=SHOT_RE.search(name)
    if not m: return ''
    d,hh,mm,ss,ap=m.groups(); h=int(hh)
    if ap.upper()=='AM': h=0 if h==12 else h
    else: h=12 if h==12 else h+12
    return f'{d}T{h:02d}:{int(mm):02d}:{int(ss):02d}'

rows=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in EXTS: continue
    low=str(p).lower()
    if 'heatseeker' not in low and 'heatmap' not in low: continue
    st=p.stat()
    dates=DATE_RE.findall(str(p))
    rows.append({
        'sha256': sha256(p),
        'basename': p.name,
        'source_path': str(p),
        'bytes': st.st_size,
        'mtime_utc': datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
        'filename_timestamp_naive': filename_ts(p.name),
        'path_date': dates[-1] if dates else '',
        'timezone_status': 'unresolved',
        'data_policy': 'observed_only',
    })

OUT.mkdir(parents=True, exist_ok=True)
jsonl=OUT/'heatseeker_source_manifest.jsonl'
csvp=OUT/'heatseeker_source_manifest.csv'
with jsonl.open('w',encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
with csvp.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['sha256'])
    w.writeheader(); w.writerows(rows)
print(json.dumps({'files':len(rows),'with_filename_time':sum(bool(r['filename_timestamp_naive']) for r in rows),'with_path_date':sum(bool(r['path_date']) for r in rows),'output':str(OUT)},indent=2))
