# Skylit — FLOOR reconstruction audit (phase 1)

Date: 2026-08-27

## Verdict court

Le `floor` Midas/Peregrine reste un **output serveur**. La formule serveur exacte n'est pas présente dans les chunks Midas/Peregrine.

Mais le corpus frontend permet maintenant de réduire fortement l'espace des hypothèses.

### CONFIRMÉ — sémantique `floor_pok`

Dans le moteur client HeatSeeker reconstruit à partir du chunk 181 :

```text
magnitude = abs(exposure)
pctOfKing = magnitude / max(magnitude)
z = (magnitude - mean(magnitude)) / stdev_population(magnitude)

significant = (z >= 1) OR (pctOfKing >= 0.25)
```

Le King a donc `pctOfKing = 1.00`.

Midas/Peregrine affiche `floor_pok` comme **node strength, King = 1.00**. Cela rend très plausible que `floor_pok` partage la même normalisation Percent-of-King, mais **le dénominateur exact du serveur Midas/Peregrine n'est pas encore prouvé** : King de la colonne 1, King d'un univers multi-expiration, ou autre univers filtré.

### CONFIRMÉ — sélection "floor-like" dans le client HeatSeeker

Dans le read client HeatSeeker, une logique d'entrée sélectionne, pour un biais bull, le **plus gros node GEX significatif à ou sous le spot**. Pour un biais bear, elle prend le symétrique au-dessus du spot.

Le même moteur contient aussi une fonction structurelle qui agrège les expositions et renvoie un `floor` comme le **plus gros GEX absolu sous le spot**, un `ceiling` comme le plus gros au-dessus, et un King par magnitude absolue.

Ces fonctions sont client-side HeatSeeker. Elles ne sont **pas** la preuve que le serveur Midas/Peregrine emploie exactement la même règle.

## Ce que Midas/Peregrine dit du floor

Le trigger plan consommé par le frontend décrit :

```text
GEX floor qualified
floor
floor_pok
node-flip => "dominant node at spot"
autres    => "front column"
```

et le texte de rationale parle d'un **Column-1 GEX floor**, avec `floor_pok`, puis d'une corroboration par **Column-2**.

Donc la famille minimale à tester est :

1. Column-1 = première expiration/front expiration.
2. POK = `abs(GEX_floor) / abs(King_de_l'univers)`.
3. Floor non-node-flip = node sous/au spot choisi dans Column-1.
4. Node-flip = dominant/King node au voisinage du spot.
5. Column-2 ne choisit pas nécessairement le floor principal : il agit comme guard/corroboration.

## Hypothèses pré-enregistrées à tester

| ID | Règle candidate | Statut avant données |
|---|---|---|
| H1 | plus gros node absolu sous/au spot dans Column-1 | À TESTER |
| H2 | node le plus proche sous/au spot dans Column-1 | À TESTER |
| H3 | plus gros node **significatif** sous/au spot, significatif = `z>=1 OR POK>=0.25` | PRIORITAIRE |
| H4 | node significatif le plus proche sous/au spot | À TESTER |
| H5 | plus gros node positif significatif sous/au spot | À TESTER, filtre de signe non établi |
| H6 | node positif significatif le plus proche sous/au spot | À TESTER |
| H7 | si King à <= 1 pas de strike du spot, floor = King (`node-flip`) | PRIORITAIRE pour classe node-flip |

## Point de prudence important

Le seuil 25%, la définition de `pctOfKing`, les fenêtres et les buckets DTE sont **confirmés pour le moteur client HeatSeeker**. Ils deviennent des candidats fortement motivés pour Midas/Peregrine, pas des constantes serveur démontrées.

De même, `rrFloor=3` du moteur client HeatSeeker ne doit pas être mélangé avec le gate `R:R >= 1:1.5` affiché par Midas/Peregrine.

## Banc d'essai créé

`skylit_floor_candidate_audit.py` compare automatiquement les règles H1-H7 à une paire synchronisée :

- matrice Gamma HeatSeeker observée ;
- setup Midas/Peregrine observé avec `floor` et `floor_pok`.

Il produit :

- `front_column_nodes.csv`
- `floor_candidates.csv`
- `audit.json`
- `AUDIT_SUMMARY.md`

Aucun GEX synthétique, aucune IV reconstruite, aucun calcul Black-Scholes et aucun positionnement dealer hypothétique.

## Critère de progression

Une règle qui matche une observation n'est que **compatible**.

Pour passer à `TESTÉ`, il faut :
- plusieurs paires synchronisées ;
- geler la règle avant le holdout ;
- mesurer taux de strike exact + erreur `floor_pok` ;
- inclure des cas `node-flip`, `king-floor`, `floor-deflection`, `washout-reclaim`;
- conserver les échecs, pas seulement les cartes qui matchent.

La prochaine donnée qui débloque réellement la formule serveur est donc une paire synchronisée `setup + GammaValues` au même timestamp.
