from pathlib import Path
import re

ROOT = Path("/Volumes/EAGET/SKYLIT_RE")
BUNDLES = ROOT / "bundles"
NOTES = ROOT / "notes"
NOTES.mkdir(exist_ok=True)

GROUPS = {
    "falcon": [r"\bfalcon\b"],
    "heatseeker": [r"heat\s*seeker", r"heatseeker"],
    "flowseeker": [r"flow\s*seeker", r"flowseeker"],
    "midas": [r"\bmidas\b"],
    "atlas": [r"\batlas\b"],
    "talon": [r"\btalon\b"],
    "athena": [r"\bathena\b"],
    "aegis": [r"\baegis\b"],
    "metrics": [
        r"\bmetrics\b",
        r"/api/contract/",
        r"/metrics",
        r"/history",
        r"/trades",
        r"/since-fill",
    ],
    "armed_fire": [
        r"\barmed\b",
        r"\bfired\b",
        r"\bfire\b",
        r"runner armed",
        r"ratchet",
        r"settled at intrinsic",
        r"max drawdown",
    ],
    "gex_vex": [
        r"\bgex\b",
        r"\bvex\b",
        r"\bgamma\b",
        r"/levels",
    ],
    "king_gatekeeper": [
        r"\bking\b",
        r"\bgatekeeper\b",
        r"\bnode\b",
        r"\bnodes\b",
    ],
    "agentzero": [
        r"agentzero",
        r"/agents/",
        r"/skills",
        r"/setups",
        r"index:flow",
    ],
}

CONTEXT = 350

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

files = [
    p for p in BUNDLES.iterdir()
    if p.is_file()
    and not p.name.startswith("._")
    and p.suffix.lower() in {".js", ".html", ".json", ".txt"}
]

summary = [
    "SKYLIT RE — BUNDLE AUDIT",
    "=" * 70,
    f"Fichiers analysés : {len(files)}",
    ""
]

file_hits = {}

for group, patterns in GROUPS.items():
    regex = re.compile("|".join(f"(?:{p})" for p in patterns), re.I)
    report = []
    occurrences = 0
    matched_files = set()

    for path in files:
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue

        matches = list(regex.finditer(text))
        if not matches:
            continue

        matched_files.add(path.name)
        occurrences += len(matches)
        file_hits.setdefault(path.name, set()).add(group)

        report += [
            "",
            "=" * 90,
            f"FILE: {path.name}",
            f"MATCHES: {len(matches)}",
            "=" * 90
        ]

        for i, m in enumerate(matches, 1):
            start = max(0, m.start() - CONTEXT)
            end = min(len(text), m.end() + CONTEXT)
            line = text.count("\n", 0, m.start()) + 1
            snippet = clean(text[start:end])

            report += [
                "",
                f"[{i}] line≈{line} offset={m.start()} match={m.group(0)!r}",
                snippet
            ]

    (NOTES / f"{group}.txt").write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    summary.append(
        f"{group:18} files={len(matched_files):3d} occurrences={occurrences:5d}"
    )

summary += ["", "BUNDLES MULTI-MODULES", "=" * 70]

for filename, groups in sorted(
    file_hits.items(),
    key=lambda x: (-len(x[1]), x[0])
):
    if len(groups) >= 2:
        summary.append(
            f"{filename:45} -> {', '.join(sorted(groups))}"
        )

routes = set()

route_re = re.compile(
    r'["\']('
    r'/api/[^"\']+'
    r'|/agents/[^"\']*'
    r'|/skills[^"\']*'
    r'|/setups[^"\']*'
    r')["\']',
    re.I,
)

for path in files:
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        continue

    for m in route_re.finditer(text):
        route = m.group(1)
        if len(route) < 250:
            routes.add(route)

(NOTES / "routes.txt").write_text(
    "\n".join(sorted(routes)),
    encoding="utf-8"
)

(NOTES / "AUDIT_SUMMARY.txt").write_text(
    "\n".join(summary),
    encoding="utf-8"
)

print("\n".join(summary))
print()
print("Rapports créés dans :", NOTES)
