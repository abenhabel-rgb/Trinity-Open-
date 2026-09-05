#!/usr/bin/env python3
import json
from pathlib import Path

PATH = Path('mu_20260904_1227_volland_like.json')
TARGETS = {955, 960, 965, 970, 975, 980, 985, 990, 995, 1000, 1005, 1010, 1015, 1020, 1025, 1030, 1035, 1040, 1045, 1050}

with PATH.open('r', encoding='utf-8') as f:
    data = json.load(f)

print('SUMMARY')
for k, v in data.get('summary', {}).items():
    print(f'{k}: {v}')

print('\nSELECTED STRIKES')
print('strike  trades  classified  unknown  unk_frac  signed_flow  signed_premium')
for row in data.get('rows', []):
    strike = row.get('strike')
    if strike in TARGETS:
        print(f"{strike:>6.1f}  {row.get('trade_count',0):>6}  {row.get('classified_contracts',0):>10}  {row.get('unknown_contracts',0):>7}  {row.get('unknown_fraction',0):>8.3f}  {row.get('signed_contract_flow',0):>11}  {row.get('signed_premium_notional',0):>14.2f}")

print('\nTOP 10 |signed contract flow|')
rows = sorted(data.get('rows', []), key=lambda r: abs(r.get('signed_contract_flow', 0)), reverse=True)[:10]
for r in rows:
    print(f"strike={r['strike']:.1f} flow={r.get('signed_contract_flow',0)} premium={r.get('signed_premium_notional',0):.2f} unknown={r.get('unknown_fraction',0):.3f}")
