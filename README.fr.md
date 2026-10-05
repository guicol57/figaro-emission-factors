# Facteurs d'émission monétaires FIGARO

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23157020.svg)](https://doi.org/10.5281/zenodo.23157020)

Facteurs d'émission de gaz à effet de serre par euro dépensé, pour 31 pays européens et 62 branches
d'activité, calculés à partir des tableaux entrées-sorties inter-pays FIGARO d'Eurostat et des
comptes d'émissions qu'Eurostat utilise pour ses empreintes officielles. Scopes 1, 2 et 3 amont, en
kgCO2e par k€ de production.

Ce dépôt contient tout le calcul : scripts, extraits de données, résultats et contrôles. Il est
maintenu par [Ecodex](https://getecodex.com), qui publie ces facteurs sous la source « FIGARO ».

[English version](README.md)

## Contenu

`results/figaro_emission_factors_26ed.csv` : 7 551 lignes, une par année (2020 à 2023), pays et
branche NACE Rév. 2 (niveau A64).

| Colonne | Signification |
|---|---|
| `total_scopes_1_2_3_upstream` | contenu amont total de 1 k€ de production : le facteur à appliquer à un montant d'achat |
| `scopes_1_2` | émissions directes de la branche et de ses fournisseurs directs d'électricité, de gaz et de vapeur |
| `scope_3_upstream` | reste de la chaîne d'approvisionnement, nationale et importée |
| `scope_1`, `scope_2` | les deux composantes de `scopes_1_2` |
| `total_co2`, `scopes_1_2_co2`, `scope_3_upstream_co2` | part CO2 ; le reste est du CH4, du N2O et des gaz fluorés |
| `total_share_domestic`, `total_share_other_eu27`, `total_share_rest_of_world` | lieu d'émission du total |
| `output_meur` | production de la branche dans FIGARO, en M€ |

Conventions : prix de base (hors taxes sur les produits, hors marges de commerce et de transport),
euros courants de l'année, principe de résidence, consommations intermédiaires seules
(immobilisations exclues), PRG des comptes d'émissions dans l'air européens (CH4 = 28, N2O = 265).

Pays : UE27, Norvège, Suisse, Royaume-Uni, Turquie. Les branches T et U et les lignes dont la
production est inférieure à 50 M€ sont écartées.

## Quand utiliser ces facteurs

Un facteur monétaire est une solution de repli : un facteur physique (par kg, kWh, km) ou une
donnée propre au fournisseur est toujours préférable quand l'achat peut être décrit ainsi. Quand
seul un montant est connu, la bonne base dépend de ce qui a été acheté et de l'endroit.

### Quelle base monétaire pour quel achat

| Votre achat | Premier choix | Pourquoi |
|---|---|---|
| Services, frais généraux ou dépenses non détaillées auprès d'un fournisseur européen | **FIGARO** | Propre à chaque pays, récent, traçable jusqu'aux statistiques officielles |
| Besoin de séparer les scopes 1 + 2 du scope 3 amont, ou de connaître la part émise hors UE | **FIGARO** | La seule de ces bases à fournir les deux décompositions |
| Un produit manufacturé, agricole ou chimique précis, tout pays | **CEDA** | 400 secteurs : ciment, élevage ou acier ne sont pas dilués dans une branche large |
| Fournisseur hors d'Europe (Asie, Amériques, Afrique, Moyen-Orient) | **CEDA** | 149 pays |
| Fournisseur aux États-Unis | **EPA Supply Chain** | 1 016 produits, modèle national |
| Fournisseur au Canada | **OpenIO-Canada** | 13 provinces et territoires, modèle national |
| Fournisseur au Japon | **MOE Japan** | Référence nationale |
| France, bilan réglementaire | Ratios monétaires de la **Base Carbone** | Référence nationale publiée par l'ADEME |
| Produits énergétiques ou traitement de déchets achetés en tant que tels | **EXIOBASE** | Produits détaillés par combustible et par filière, données 2019 |

Un modèle national, quand il existe pour le pays du fournisseur, est en général le meilleur point
de départ ; FIGARO et CEDA sont les deux options qui couvrent de nombreux pays avec une méthode
homogène.

### Ce qui distingue les bases

Telles que disponibles dans Ecodex en octobre 2026.

| Base | Pays | Secteurs | Années | Base de prix | Méthode en une ligne |
|---|---|---|---|---|---|
| **FIGARO** (ce dépôt) | 31 pays européens | 62 branches | 2020-2023, annuel | Prix de base | Tableaux inter-pays et comptes d'émissions d'Eurostat |
| CEDA (Watershed) | 149 | 400 secteurs | 2021-2024 | Prix d'achat | Modèle mondial, une année de base d'émissions réindexée par année |
| EXIOBASE v3.8.2 | 48 pays et régions | 184 produits | 2019 | Prix de base | Modèle multirégional mondial, consortium académique |
| EPA Supply Chain v1.4 | États-Unis | 1 016 produits | USD 2024 | Prix d'achat | Modèle national USEEIO |
| OpenIO-Canada | Canada, 13 provinces et territoires | 472 produits | 2022 | voir la source | Modèle national, immobilisations incluses |
| Ratios monétaires Base Carbone | France | 56 produits | 2019-2023 | Prix de base | Contenus importés FIGARO et comptes nationaux de l'Insee (SDES) |
| MOE Japan | Japon | environ 540 postes | jusqu'à 2020 | voir la source | Référence nationale |

Trois différences expliquent l'essentiel des écarts entre deux facteurs pour le « même » achat :

- **La base de prix.** Le prix de base exclut les taxes sur les produits et les marges de commerce
  et de transport ; le prix d'achat les inclut. Les mêmes émissions divisées par un montant plus
  grand donnent un facteur plus bas.
- **Le détail sectoriel.** Avec 62 branches, un même facteur regroupe le ciment et le verre, ou
  l'élevage et les céréales.
- **Le périmètre du modèle.** Certains modèles incluent les immobilisations, la plupart non ; les
  années et les inventaires d'émissions diffèrent.

### Repères pour FIGARO

- Adapté : services et dépenses non détaillées dans un pays européen, quand on veut un facteur
  traçable jusqu'aux statistiques officielles.
- Peu adapté : un produit industriel ou agricole précis (voir le tableau ci-dessus).
- France : les ratios de la Base Carbone sont environ 15 % plus élevés que ces facteurs, pour une
  raison documentée (voir Contrôles).
- Un montant TTC ou incluant des marges commerciales surestime les émissions avec des facteurs au
  prix de base.
- Ne pas changer de base d'une année sur l'autre pour une même catégorie de dépenses : le
  changement de base apparaîtrait comme une variation d'émissions.

## Méthode

`figaro_core.py`, une centaine de lignes :

```
x  production par (pays, branche)                  M€
A  = Z / x        coefficients techniques
f  = E / x        intensité d'émission directe      scope 1
m  = f (I - A)^-1 intensité amont totale            scopes 1 + 2 + 3 amont
scope 2        = émissions directes des fournisseurs D35 (électricité, gaz, vapeur) par unité de
                 leurs ventes directes à la branche, tous pays d'origine (approche géographique)
scope 3 amont  = m - scope 1 - scope 2
```

La part CO2 est le même calcul avec les seules émissions de CO2. Le lieu d'émission regroupe les
lignes de `f (I - A)^-1` par pays émetteur.

### Données d'entrée

| Donnée | Source Eurostat |
|---|---|
| Tableau entrées-sorties inter-pays, branche par branche, 64 branches x 50 régions, édition 2026 | FIGARO, [espace public CIRCABC](https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database) (48 Mo par année, téléchargé par `fetch_eurostat.py --tables`) |
| Émissions directes de GES et de CO2 par pays et branche | `env_ac_ghgfp`, `env_ac_co2fp` avec `c_dest=WORLD`, `na_item=TOTAL` |
| Contrôles : empreintes officielles, comptes d'émissions dans l'air, production des comptes nationaux, TES symétrique français | `env_ac_ghgfp`, `env_ac_ainah_r2`, `nama_10_a64`, `naio_10_cp1700` |
| Contrôle : contenu amont en GES des produits français, tableau GES.501 | [SDES / Insee](https://www.statistiques.developpement-durable.gouv.fr/emissions-de-gaz-effet-de-serre-et-empreinte-carbone-de-la-france-une-baisse-significative-en-2023) |

Les émissions des pays hors UE sont les estimations fondées sur EDGAR produites par Eurostat
lui-même (note méthodologique « FIGARO - Greenhouse gas emission estimates »). Aucun modèle
d'émissions tiers n'est ajouté. L'Albanie, le Monténégro, la Macédoine du Nord et la Serbie sont
fusionnés dans le reste du monde, comme dans les comptes d'émissions publiés. Les requêtes et les
dates de mise à jour Eurostat de chaque extrait sont consignées dans `data/SOURCES.csv`.

### Éditions

Tableaux : édition 2026 (juin 2026). Émissions : publication Eurostat de janvier 2026, qui s'arrête
à 2023 ; **2023 est donc la dernière année**. Les comptes d'émissions dans l'air européens ne
dépendent pas de l'édition de FIGARO ; les estimations hors UE ont été ventilées par Eurostat avec
l'édition 2025. Le passage des tableaux de l'édition 2025 à l'édition 2026 modifie les facteurs
européens 2022-2023 de +0,3 % en médiane, 56 % d'entre eux restant à 5 % près et 9 % bougeant de
plus de 20 % (révisions des comptes nationaux).

## Contrôles

Rapports dans `results/<édition>/validation/`.

1. **Empreintes officielles d'Eurostat.** Appliqués à la demande finale FIGARO, les multiplicateurs
   redonnent l'empreinte publiée par Eurostat pour chaque pays : avec l'édition 2025, celle utilisée
   par Eurostat, ratio médian 1,0000, 96 % des 46 régions à 1 % près, écart maximal 2,1 %
   (`results/25ed`). Les tableaux de l'édition 2025 ne sont plus distribués, ce contrôle ne peut donc
   plus être relancé à partir de fichiers publics ; avec les tableaux 2026 l'accord n'est plus exact
   (35 à 48 % des régions à 1 % près).
2. **Scope 1.** Les émissions sont égales aux comptes d'émissions dans l'air pour 95 à 97 % des
   lignes ; l'intensité directe est à 5 % près de comptes / production des comptes nationaux pour
   96 à 99 % des lignes, médiane 1,000.
3. **France, comparaison au tableau GES.501 du SDES et de l'Insee**, dont les valeurs sont celles
   que l'ADEME publie comme ratios monétaires :
   - ces facteurs : ratio médian de 0,82 à 0,87 selon l'année ;
   - contenus importés FIGARO combinés au tableau entrées-sorties national français, ce qui
     approche la méthode du SDES : médiane de 0,94 à 0,96, 70 à 79 % des branches à 10 % près.

### Pourquoi la France est environ 15 % sous la Base Carbone

Les émissions directes françaises sont les mêmes des deux côtés. Le SDES remplace le bloc France de
FIGARO par les comptes nationaux de l'Insee et ne garde de FIGARO que le contenu des produits
importés. Les biens importés utilisés par les branches françaises sont plus faibles dans FIGARO que
dans les comptes nationaux (60 à 80 % du montant selon le produit en 2022), parce que FIGARO
arbitre les asymétries des statistiques du commerce international. Des tableaux nationaux de ce
type n'existent que pour une douzaine de pays par an : le même ajustement ne peut pas être appliqué
de façon homogène en Europe, et ces facteurs restent calculés sur FIGARO seul.

La comparaison avec CEDA et EXIOBASE est dans [docs/comparison-ceda-exiobase.md](docs/comparison-ceda-exiobase.md) (en anglais).

## Reproduire

```
pip install -r requirements.txt
python fetch_eurostat.py --tables tables      # extraits Eurostat dans data/, tableaux FIGARO dans tables/
python build_factors.py --figaro-dir tables   # results/26ed/ (46 régions, non versionné)
python validate.py                            # results/26ed/validation/
python build_results.py                       # results/figaro_emission_factors_26ed.csv
```

Environ 2 minutes et 4 Go de mémoire une fois les tableaux téléchargés. Eurostat écrase ses jeux de
données en place : relancer `fetch_eurostat.py` plus tard peut renvoyer des données révisées ; les
extraits versionnés dans `data/` sont ceux des résultats publiés.

## Limites

- 64 branches, technologie moyenne de chaque branche dans chaque pays.
- Tableaux et estimations d'émissions proviennent de deux éditions consécutives de FIGARO.
- Les petits pays et les petites branches donnent des ratios instables malgré le seuil de 50 M€.
- Seule la distinction CO2 / autres gaz est possible sur toute la chaîne.
- Le scope 2 est en approche géographique et de premier rang ; D35 regroupe électricité, gaz et vapeur.

## Licence et attribution

Code : MIT, voir `LICENSE`. Résultats et documentation : CC BY 4.0, voir `DATA_LICENSE.md`, qui
précise aussi l'attribution due à Eurostat et au SDES / Insee pour les données d'entrée.

Pour citer : voir `CITATION.cff`. Archivé sur Zenodo : toutes versions https://doi.org/10.5281/zenodo.23157020, version 2026.1 https://doi.org/10.5281/zenodo.23157021.
