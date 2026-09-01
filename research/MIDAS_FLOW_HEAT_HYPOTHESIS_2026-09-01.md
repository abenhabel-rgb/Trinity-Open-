# H_MIDAS_FLOW_HEAT_GATE_V0 — préenregistrement

Date de gel : 2026-09-01

## Statut

**HYPOTHESIS — non validée économiquement.**

Cette hypothèse est dérivée d'interfaces et de publications déjà observées. Le
code associé est une reconstruction mécanique destinée à la falsification.

## Hypothèse

Un flow directionnel identifie le ticker/contrat potentiel. Une confirmation
Heatseeker observée, initialement limitée à `NODE_FLIP`, retarde l'entrée. Ce
retard doit réduire le drawdown au bid sans supprimer l'essentiel du MFE du flow.

## Baseline et traitement

- Baseline : entrée au premier ask observé à/après le timestamp flow.
- Traitement : entrée au premier ask observé à/après le timestamp Heat.
- Sortie commune : dernier bid observé avant `evaluation_end_et`, fixé avant le
  calcul des résultats.

## Critère primaire proposé

Sur au moins 30 candidats `TRIGGERED`, couvrant au moins 20 séances intactes :

1. amélioration MAE moyenne strictement positive ;
2. borne basse de l'IC bootstrap 95 % par séance strictement positive ;
3. rétention MFE moyenne d'au moins 0,80.

Le troisième seuil est une spécification de recherche gelée, pas une propriété
connue du système étudié.

## Falsification

L'hypothèse est falsifiée pour cette version si l'une des conditions suivantes
est satisfaite sur l'OOS :

- l'IC 95 % de l'amélioration MAE inclut zéro ou devient négatif ;
- la rétention MFE moyenne est inférieure à 0,80 ;
- les résultats nécessitent de changer les timestamps, le trigger, l'univers ou
  l'heure de sortie après observation des outcomes.

## Dates exclues de l'OOS

- META : seed 2026-06-25, outcome observé 2026-07-01.
- Toute séance déjà utilisée pour choisir `NODE_FLIP`, les seuils ou le schéma
  de données doit être ajoutée ici avant le prochain test.

## Données obligatoires

- preuve Flow et timestamp ET ;
- preuve Heat et timestamp ET ;
- contrat exact ;
- NBBO observés couvrant les deux entrées et la sortie commune ;
- provenance de chaque événement ;
- statut `BLOCKED` si une pièce manque.

## Séparation des conclusions

- reproduire le lifecycle = reconstruction mécanique ;
- réduire le MAE au bid = résultat statistique ;
- produire un rendement net robuste OOS = validation économique distincte.
