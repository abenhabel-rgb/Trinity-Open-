# Midas Flow → Heat Gate

## Objet

Ce module formalise une hypothèse de recherche dérivée de descriptions publiques
de l'interface étudiée :

```text
Flowseeker indique QUOI acheter.
Heatseeker indique QUAND acheter.
Midas orchestre le lifecycle SEEDED/WATCHING/TRIGGERED.
```

Il ne reproduit pas un produit commercial, ne calcule pas GEX/VEX et ne prédit
pas le marché. Il compare deux règles sur les mêmes événements observés :

1. **FLOW_IMMEDIATE** — achat de l'option au premier ask observé après le flow ;
2. **HEAT_GATED** — achat au premier ask observé après un événement Heat autorisé.

Les deux chemins sont liquidés au bid et partagent une heure de fin déclarée à
l'avance. Le but est de tester si le gate Heat réduit le drawdown sans supprimer
l'excursion favorable du flow.

## Lifecycle

```text
flow observé → SEEDED/WATCHING
                    ├─ trigger absent ou refusé → WATCHING
                    ├─ données manquantes       → BLOCKED
                    └─ trigger autorisé          → TRIGGERED
```

Le seul événement accepté par défaut est `NODE_FLIP`. `breadth_confirmed` n'est
exigé que si `--require-breadth` est explicitement activé : aucune feature
inconnue n'est imputée silencieusement.

## Entrées

### `events.csv`

Colonnes obligatoires :

| Colonne | Description |
| --- | --- |
| `candidate_id` | Identifiant stable de l'événement |
| `ticker` | Sous-jacent |
| `contract` | Contrat exact, conservé comme texte |
| `direction` | `BULL` ou `BEAR` |
| `flow_time_et` | Timestamp ISO-8601 du flow, avec offset ET |
| `heat_time_et` | Timestamp ISO-8601 du trigger ; vide si absent |
| `evaluation_end_et` | Fin commune, préenregistrée, des deux stratégies |
| `flow_observed` | Booléen ; aucune donnée dérivée admise |
| `heat_observed` | Booléen ; aucune donnée dérivée admise |
| `heat_event` | Par exemple `NODE_FLIP` |
| `breadth_confirmed` | Booléen observé |
| `flow_source` | Référence exacte de la preuve flow |
| `heat_source` | Référence exacte de la preuve Heat |

Colonnes optionnelles, uniquement si fournies par la source : `node_level`,
`net_gex`, `net_vex`. Elles sont reportées mais jamais recalculées ni utilisées
implicitement par le gate.

Exemple :

```csv
candidate_id,ticker,contract,direction,flow_time_et,heat_time_et,evaluation_end_et,flow_observed,heat_observed,heat_event,breadth_confirmed,flow_source,heat_source,node_level,net_gex,net_vex
demo-001,XYZ,XYZ 100C 2026-10-16,BULL,2026-09-04T10:00:00-04:00,2026-09-04T10:20:00-04:00,2026-09-04T15:55:00-04:00,true,true,NODE_FLIP,true,uw:print-id,heat:frame-id,100,,
```

### `quotes.csv`

NBBO observés du contrat exact :

```csv
candidate_id,timestamp_et,bid,ask
demo-001,2026-09-04T10:00:00-04:00,2.35,2.45
demo-001,2026-09-04T10:20:00-04:00,1.95,2.05
demo-001,2026-09-04T15:55:00-04:00,2.80,2.95
```

Les timestamps sans fuseau, quotes croisées, sources absentes et données non
numériques sont refusés.

## Exécution

Depuis la racine du dépôt :

```bash
PYTHONPATH=src python3 -m trinity.midas_flow_heat_gate \
  --events data/midas/events.csv \
  --quotes data/midas/quotes.csv \
  --out reports/midas_gate_rows.csv \
  --summary reports/midas_gate_summary.json \
  --require-breadth
```

Les dossiers `data/` et `reports/` doivent rester locaux et ne pas recevoir de
clés, de fichiers OPRA bruts ou de données sous licence dans GitHub.

## Mesures

- `MAE` : pire rendement au bid depuis l'ask d'entrée ;
- `MFE` : meilleur rendement au bid depuis l'ask d'entrée ;
- rendement final : bid de fin contre ask d'entrée ;
- amélioration MAE : `MAE_gated - MAE_flow` ; positif = drawdown réduit ;
- rétention MFE : `MFE_gated / MFE_flow` lorsque le MFE flow est positif ;
- intervalle bootstrap 95 % par séance, afin de ne pas considérer plusieurs
  contrats corrélés d'une même séance comme totalement indépendants.

## Limites

- Un statut `TRIGGERED` est une reconstruction déterministe à partir des entrées,
  pas la preuve qu'un ordre réel a été exécuté.
- `max`, `last` ou `mid` ne remplacent jamais le bid/ask observable.
- Le script n'infère pas le signe dealer, la convention NetVEX ou un score Midas.
- Une baisse du drawdown sans lift économique hors échantillon ne valide pas la
  stratégie.
- Le cas META du 25 juin / 1er juillet 2026 est une date déjà vue et ne peut pas
  servir d'OOS.

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Les tests couvrent le calcul au bid/ask, les états `WATCHING/TRIGGERED`, le gate
breadth explicite et le refus des timestamps ambigus.
