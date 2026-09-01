# Trinity 10-Minute Regime Gate

## Objet

Ce module formalise une seule affirmation observée dans une publication Skylit :
un jour de tendance haussière aurait été identifiable dans les dix premières
minutes grâce à la confluence suivante :

- SPX : air pocket et route dégagée vers le haut ;
- SPY : floor testé puis tenu ;
- QQQ : floor testé puis tenu.

La publication citait notamment les floors SPY 751 et QQQ 686. Ces niveaux sont
des exemples déjà vus, pas des constantes du modèle.

Le script ne lit pas une image, ne reconstruit pas GEX/VEX et ne décide pas
qu'un air pocket existe. Ces observations doivent être fournies avec leur
timestamp et leur provenance par un export, un HAR, une API autorisée ou une
annotation humaine vérifiable.

## Règle gelée V0

Un résultat `TREND_UP` exige simultanément :

1. une décision comprise entre l'ouverture et `open + 10 minutes` ;
2. `spx_air_pocket_up=true` ;
3. `spx_route_clear=true` ;
4. floor SPY testé et tenu, spot au-dessus du floor à 5 bp près ;
5. floor QQQ testé et tenu, spot au-dessus du floor à 5 bp près ;
6. une source non vide pour SPX, SPY et QQQ.

La tolérance de 5 bp traite uniquement un faible décalage entre snapshots. Elle
est exposée par `--floor-tolerance-bps` et doit être figée avant un test OOS.

| Statut | Signification |
| --- | --- |
| `TREND_UP` | Toutes les conditions V0 sont observées avant la coupure |
| `UNCONFIRMED` | Données complètes, mais une condition directionnelle échoue |
| `BLOCKED` | Timestamp, source ou feature indispensable manquant/inexploitable |

`UNCONFIRMED` ne signifie pas `RANGE`. Une règle range distincte n'a pas encore
été spécifiée.

## Schéma d'entrée

Le fichier `observations.csv` contient une ligne par séance :

| Colonne | Contenu |
| --- | --- |
| `session_id` | Identifiant stable de la séance |
| `market_open_et` | Ouverture au format ISO-8601 avec offset |
| `decision_time_et` | Heure exacte à laquelle les features sont gelées |
| `spx_air_pocket_up` | Observation booléenne, jamais imputée |
| `spx_route_clear` | Absence observée de blocage majeur sur la route |
| `spy_spot`, `spy_floor` | Spot et floor SPY au timestamp de décision |
| `spy_floor_tested`, `spy_floor_held` | État observé du floor SPY |
| `qqq_spot`, `qqq_floor` | Spot et floor QQQ au timestamp de décision |
| `qqq_floor_tested`, `qqq_floor_held` | État observé du floor QQQ |
| `spx_source`, `spy_source`, `qqq_source` | Références des preuves |
| `notes` | Champ optionnel |

Exemple mécanique :

```csv
session_id,market_open_et,decision_time_et,spx_air_pocket_up,spx_route_clear,spy_spot,spy_floor,spy_floor_tested,spy_floor_held,qqq_spot,qqq_floor,qqq_floor_tested,qqq_floor_held,spx_source,spy_source,qqq_source,notes
demo-001,2026-09-04T09:30:00-04:00,2026-09-04T09:39:00-04:00,true,true,750.74,751,true,true,687.39,686,true,true,frame:spx,frame:spy,frame:qqq,fixture
```

Les valeurs vides deviennent `BLOCKED`. Les booléens inconnus ne deviennent
jamais implicitement `false` ou `true`.

## Exécution

Depuis la racine du dépôt :

```bash
PYTHONPATH=src python3 -m trinity.trinity_10m_regime_gate \
  --observations data/trinity/observations.csv \
  --out reports/trinity_10m_rows.csv \
  --summary reports/trinity_10m_summary.json
```

Le CSV de sortie conserve chaque feature, les distances spot/floor, le motif du
statut et les trois sources. Le JSON agrège seulement les statuts. Aucun outcome
n'est lu par cette version.

## Place dans l'architecture

```text
Flow     = quel candidat surveiller
Trinity  = quel régime inter-books est observé
Heat     = quand le déclenchement devient acceptable
Midas    = lifecycle et gestion de l'entrée
```

`TREND_UP` peut devenir une feature d'un futur gate Midas. Il ne constitue pas
à lui seul un ordre d'achat.

## Limites et validation

- La publication et ses captures constituent une preuve de spécification après
  observation du mouvement, pas un test prédictif.
- La séance montrée est brûlée pour choisir cette logique et ses tolérances.
- L'heure de marché exacte de la capture doit encore être récupérée ; elle ne
  doit pas être inventée à partir de l'heure de la capture d'écran.
- Les labels `air_pocket` et `route_clear` doivent ensuite être remplacés par une
  extraction reproductible si le schéma Heatseeker correspondant est obtenu.
- Une reconstruction mécanique correcte n'est jamais une validation économique.

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Les tests couvrent la confluence, la coupure à dix minutes, la tolérance du
floor, les données manquantes et l'exécution CSV complète.
