# H_TRINITY_10M_TREND_UP_V0 — préenregistrement

Date de gel : 2026-09-01

## Statut

**HYPOTHESIS — signal mécanique spécifié, validation économique bloquée.**

## Affirmation testable

Une confluence observée avant la fin des dix premières minutes — air pocket et
route haussière SPX, floors SPY et QQQ testés puis tenus — identifie un régime
`TREND_UP` plus souvent suivi d'une continuation haussière que la baseline.

## Spécification V0

- Fenêtre : ouverture ET à ouverture + 10 minutes incluses.
- Floor tenu : spot au-dessus du niveau à 5 bp près au timestamp gelé.
- SPX : `air_pocket_up=true` et `route_clear=true` observés.
- SPY et QQQ : `floor_tested=true` et `floor_held=true` observés.
- Aucune feature manquante, reconstruite ou imputée.
- Provenance obligatoire pour les trois books.

## Baseline et outcome

La baseline, l'instrument tradé, l'heure de sortie et les coûts ne sont pas
encore gelés. Ils doivent l'être avant le premier test prédictif. Jusqu'à cette
décision, le script ne calcule volontairement aucun taux de réussite ni P/L.

## Falsification de la reconstruction

La reconstruction V0 échoue si :

- le même CSV ne reproduit pas toujours le même statut ;
- une donnée manquante produit `TREND_UP` ;
- un signal situé après la coupure de dix minutes est accepté ;
- le résultat dépend d'un outcome ou d'une valeur calculée après la décision.

## Conditions avant validation économique

1. geler l'outcome et la baseline ;
2. collecter des snapshots intacts avant 09:40 ET ;
3. conserver toutes les séances, y compris les absences de signal ;
4. évaluer sur des dates non utilisées pour écrire la règle ;
5. comparer le lift net de coûts et fournir un intervalle d'incertitude.

## Données brûlées

- La publication Skylit montrant SPY 751, QQQ 686 et la continuation haussière.
- Date de publication/capture observée : 2026-09-01.
- Date exacte de la séance de marché : **BLOCKED — non visible dans les preuves
  disponibles**.

## Séparation obligatoire

- `TREND_UP` reproductible = reconstruction mécanique ;
- continuation supérieure à une baseline OOS = résultat statistique ;
- rendement net robuste et exploitable = validation économique distincte.
