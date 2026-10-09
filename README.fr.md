# Facteurs d'émission monétaires FIGARO

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23157020.svg)](https://doi.org/10.5281/zenodo.23157020)

Facteurs d'émission de gaz à effet de serre par euro dépensé, pour 31 pays européens et 62 branches
d'activité, calculés à partir des tableaux entrées-sorties inter-pays FIGARO d'Eurostat et des
comptes d'émissions qu'Eurostat utilise pour ses empreintes officielles. Scopes 1, 2 et 3 amont, en
kgCO2e par k€ de production, selon deux vues : le pays de **production** (où les biens ou services
sont produits) et le pays de **demande** (ce qu'un pays achète réellement, production nationale et
importations), et la vue demande convertie au **prix d'achat** que paient réellement les entreprises.

Ce dépôt contient tout le calcul : scripts, extraits de données, résultats et contrôles. Il est
maintenu par [Ecodex](https://getecodex.com), qui publie ces facteurs au sein de la source « Eurostat ».

[English version](README.md)

## Contenu

`results/figaro_emission_factors_26ed.csv` : 20 541 lignes, une par année, pays et branche NACE
Rév. 2 (niveau A64) : 2014 à 2023 complètes, 2024 provisoire avec les scopes 1 + 2 seulement.

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

`results/figaro_demand_emission_factors_26ed.csv` : 18 465 lignes, une par année, pays acheteur et
produit, 2014 à 2023. Mêmes colonnes de valeurs, moyennées sur tous les pays d'origine, plus :

| Colonne | Signification |
|---|---|
| `purchases_meur` | consommation intermédiaire du produit par les branches du pays, en M€ |
| `purchases_share_domestic`, `purchases_share_other_eu27`, `purchases_share_rest_of_world` | provenance de ces achats |
| `total_share_domestic`, `total_share_other_eu27`, `total_share_rest_of_world` | lieu d'émission du total, vu du pays acheteur |

Les lignes dont les achats sont inférieurs à 50 M€ sont écartées.

`results/figaro_final_demand_emission_factors_26ed.csv` : 17 709 lignes, même structure que la table de
demande, pondérée par les achats **finals** du pays (consommation des ménages, des administrations et des
ISBLSM, formation brute de capital fixe ; variations de stocks exclues) au lieu des consommations
intermédiaires de ses branches. `purchases_meur` désigne alors les achats finals.

`results/figaro_supply_chain_details_26ed.csv` : 18 834 lignes, une par ligne de la table de production,
2014 à 2023 :

| Colonne | Signification |
|---|---|
| `share_own_operations`, `share_tier_1`, `share_tier_2`, `share_tier_3_plus` | décomposition du total par rang de la chaîne d'approvisionnement : la branche elle-même, ses fournisseurs directs, leurs fournisseurs, et au-delà |
| `total_with_aviation_rf` | total avec le forçage radiatif de l'aviation (CO2 direct du transport aérien x 1,7), optionnel |

`results/figaro_purchaser_price_factors_26ed.csv` : 13 495 lignes, une par année, pays acheteur et
produit, 2014 à 2023, pour les 26 pays qui publient des matrices de passage (voir Prix d'achat).

| Colonne | Signification |
|---|---|
| `total_purchaser_prices_with_margins` | facteur du pays de demande par k€ au prix d'achat, émissions des marges de commerce et de transport incluses : le facteur à appliquer à un montant facturé hors TVA déductible |
| `total_purchaser_prices_rebased` | mêmes émissions que le facteur au prix de base, divisées par le prix d'achat (marges sans émissions) |
| `total_basic_prices` | le facteur de la table de demande |
| `rebasing_ratio`, `margin_term` | pour convertir n'importe quel facteur du produit au prix de base : `facteur x rebasing_ratio + margin_term` |
| `share_basic_value`, `share_trade_transport_margins`, `share_taxes_less_subsidies` | décomposition du prix d'achat payé par les branches du pays |
| `margin_factor`, `margins_transport_share` | facteur des services de marge (mix commerce et transport du pays) et part du transport dans ce mix |
| `valuation_year`, `purchases_pp_meur` | année des tableaux nationaux utilisés, et achats au prix d'achat cette année-là (M€) |

## Quand utiliser ces facteurs

Un facteur monétaire est une solution de repli : un facteur physique (par kg, kWh, km) ou une
donnée propre au fournisseur est toujours préférable quand l'achat peut être décrit ainsi. Quand
seul un montant est connu, la bonne base dépend de ce qui a été acheté et de l'endroit.

### Pays de production ou pays de demande

Le facteur de production d'un pays porte sur 1 k€ produit dans ce pays. Le facteur de demande porte
sur 1 k€ de ce que les branches de ce pays achètent du produit, toutes origines confondues : c'est la
moyenne des facteurs de production de toutes les origines, pondérée par les achats réels.

Textile, habillement et cuir (C13-15), 2023, kgCO2e par k€ :

| | Facteur | |
|---|---|---|
| France, pays de production | 205 | fabriqué en France |
| France, pays de demande | 369 | 36 % acheté en France, 30 % dans le reste de l'UE, 34 % hors UE |
| Chine, pays de production | 724 | |
| Inde, pays de production | 1 347 | |

- **Origine de l'achat connue** : table de production, pays du fournisseur (ou du fabricant, pour un
  revendeur).
- **Origine inconnue** : table de demande, pays de l'entreprise acheteuse.
- **Achats des entreprises ou achats finals.** La table de demande est pondérée par ce qu'achètent les
  branches : à utiliser pour les intrants de production et les services. Pour des biens finis ou des
  équipements achetés en tant que tels (vêtements, véhicules, ordinateurs, mobilier), dont le mix
  d'origine suit les achats de consommation et d'investissement, la table de demande finale est plus
  proche. Les deux sont à quelques pourcents l'une de l'autre pour la plupart des produits (ratio médian
  1,00 pour les biens, 0,99 pour les services en 2023) et s'écartent pour certains biens finis importés :
  Royaume-Uni, textile, 2023, 391 pondéré par les achats des entreprises, 553 par les achats finals.
- Le commerce de détail (G47) n'est pas un substitut : au prix de base il ne couvre que la marge
  commerciale (magasins, leur énergie et leur logistique), jamais les biens vendus. Un achat au prix
  d'achat se décompose en valeur des biens au prix de base (facteur du produit), marges de commerce et
  de transport (facteurs de G et H) et taxes : la table au prix d'achat fait cette décomposition pour
  les achats des entreprises.

Les deux vues sont proches pour les services, achetés surtout localement (2023 : écart médian de
3 %, deux couples sur trois à 10 % près), et s'écartent pour les biens (écart médian de 11 %, 42 % à
10 % près), surtout importés : textile, électronique, chimie, métaux, produits des industries
extractives.

### Quelle base monétaire pour quel achat

| Votre achat | Premier choix | Pourquoi |
|---|---|---|
| Services, frais généraux ou dépenses non détaillées auprès d'un fournisseur européen | **FIGARO** | Propre à chaque pays, récent, traçable jusqu'aux statistiques officielles |
| Un achat européen dont le pays d'origine est inconnu | **FIGARO**, pays de demande | Moyenne de toutes les origines, pondérée par ce que le pays achète réellement |
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
| **FIGARO** (ce dépôt) | 31 pays européens | 62 branches | 2014-2023, annuel (2024 : scopes 1 + 2) | Prix de base ; prix d'achat des entreprises dans 26 pays | Tableaux inter-pays et comptes d'émissions d'Eurostat |
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
- Un montant facturé est au prix d'achat : avec un facteur au prix de base il surestime les émissions
  (biens : environ 9 % en médiane, plus de 25 % pour une ligne sur dix). Utiliser la table au prix
  d'achat, ou `rebasing_ratio` et `margin_term` avec un facteur de production quand l'origine est
  connue. Un montant incluant la TVA déductible surestime dans tous les cas.
- Ne pas changer de base d'une année sur l'autre pour une même catégorie de dépenses : le
  changement de base apparaîtrait comme une variation d'émissions.

## Méthode

`figaro_core.py`, environ 200 lignes :

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

Pays de demande, pour un pays acheteur s et un produit p :

```
w(r | s, p)   = part de l'origine r dans les achats intermédiaires de p par les branches de s
                (flux FIGARO, nationaux et importés)
demande(s, p) = somme sur les origines r de w(r | s, p) x m(r, p)     mêmes poids pour chaque scope
```

Les poids sont les achats des entreprises (consommations intermédiaires), pas la demande finale des
ménages. Toutes les origines y entrent, y compris les lignes écartées de la table de production.
`build_factors.py` vérifie que les facteurs de demande multipliés par les achats redonnent les
émissions contenues dans les achats de chaque pays.

### Achats finals, rangs de la chaîne, aviation

- **Achats finals.** Même formule que le pays de demande, avec les achats finals de s comme poids :
  consommation des ménages, des administrations et des ISBLSM et formation brute de capital fixe
  (`P3_S13`, `P3_S14`, `P3_S15`, `P51G`) ; les variations de stocks (`P5M`) sont exclues, les cellules de
  FBCF négatives (cessions) ramenées à 0. `build_factors.py` vérifie que
  les facteurs multipliés par les achats finals redonnent les émissions qu'ils contiennent.
- **Rangs de la chaîne.** `m = f + f A + f A^2 + ...` : émissions propres de la branche (f), de ses
  fournisseurs directs (f A, qui contient le scope 2), de leurs fournisseurs (f A^2), et le reste. Une ACV
  de procédés qui s'arrête après quelques rangs manque la dernière couche (37 à 40 % du total en
  médiane) : la décomposition montre où un facteur entrées-sorties peut la compléter (ACV hybride).
- **Forçage radiatif de l'aviation.** Désactivé par défaut, comme dans le GHG Protocol et les comptes
  d'émissions dans l'air. `total_with_aviation_rf` multiplie le CO2 direct du transport aérien (H51) par
  1,7, la valeur centrale de la
  [méthodologie 2026 du DESNZ britannique](https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
  (paragraphes 2.10 et 8.39 à 8.43, CO2 seul), sur toute la chaîne : `(1,7 - 1) x f_CO2,H51 (I - A)^-1`.
  Le multiplicateur est indicatif et incertain (même source) : le présenter à part, jamais à la place du
  total.

### Prix d'achat

Les facteurs ci-dessus sont par euro au prix de base. Une entreprise paie la valeur du produit au prix
de base, plus les marges de commerce et de transport de ses distributeurs, plus les impôts nets des
subventions sur les produits. Eurostat publie, par pays et par année, les tableaux des emplois au prix
d'acquisition et au prix de base et les deux matrices de passage entre eux, par produit et par
utilisateur. `build_purchaser_prices.py` les prend sur les consommations intermédiaires de toutes les
branches, pour un pays acheteur s et un produit p :

```
PA           = PB + M + T                              tableaux nationaux, achats des entreprises
FE_M(s)      = somme sur les services de marge k de w_k x m(s, k)
               w_k = part de k (G45-G47, H49-H53) dans les marges du tableau des ressources de s
avec marges  = (PB x FE_PB + M x FE_M(s) + T x 0) / PA  = FE_PB x PB / PA + M / PA x FE_M(s)
rebasé       = FE_PB x PB / PA
```

FE_PB est le facteur du pays de demande. Achats des entreprises, et non ressources totales : en 2022,
le textile coûte aux branches françaises qui l'achètent 1,41 fois sa valeur au prix de base, contre
1,79 fois en moyenne sur tous les emplois, ménages compris (marges du commerce de détail). Même approche
que les facteurs de l'EPA américaine avec et sans marges.

Textile, habillement et cuir (C13-15) acheté en France, 2023, kgCO2e par k€ : 369 au prix de base,
261 rebasé, 295 avec marges (matrices de passage 2022 : 71 % valeur au prix de base, 26 % marges, 3 % taxes).

- La matrice des marges donne le total des marges. Leur partage entre services de commerce et de
  transport est celui du tableau des ressources du pays, le même pour tous les produits (le transport
  représente 6 % des marges en médiane). Valoriser toutes les marges au facteur du commerce de gros
  change le résultat de moins de 2 % pour 96 % des lignes (contrôle 5).
- Les taxes ne portent pas d'émissions. Elles comprennent la TVA non déductible : en France en 2022,
  les branches exonérées de TVA (finance, assurance, administration, enseignement, santé) paient des
  taxes de 15 % de la valeur au prix de base sur les services informatiques qu'elles achètent, contre
  2,6 % pour l'ensemble des branches. La table fait la moyenne de toutes les branches : elle sous-estime
  légèrement le facteur pour un acheteur qui déduit toute sa TVA (+0,4 % en médiane, +3 % au p90, hors
  branches exonérées).
- Les matrices de passage ne sont obligatoires que tous les 5 ans : une année sans elles prend l'année
  la plus proche du même pays, à 5 ans au plus (`valuation_year`, 66 % des lignes utilisent la même
  année). L'Allemagne, l'Espagne, la Bulgarie, la Suisse et le Royaume-Uni n'en publient pas (ou pas les
  marges et les taxes) : pas de lignes.
- Les services de marge achetés en tant que tels (commissions de gros, fret) ne portent pas de marge
  propre. Quand la matrice des marges manque mais que les trois autres tableaux sont publiés, marges =
  PA - PB - taxes ; les cellules où les quatre tableaux divergent de plus de 1 % sont écartées.

### Données d'entrée

| Donnée | Source Eurostat |
|---|---|
| Tableau entrées-sorties inter-pays, branche par branche, 64 branches x 50 régions, édition 2026 | FIGARO, [espace public CIRCABC](https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database) (48 Mo par année, téléchargé par `fetch_eurostat.py --tables`) |
| Émissions directes de GES et de CO2 par pays et branche | `env_ac_ghgfp`, `env_ac_co2fp` avec `c_dest=WORLD`, `na_item=TOTAL` |
| Contrôles : empreintes officielles, comptes d'émissions dans l'air, production des comptes nationaux, TES symétrique français | `env_ac_ghgfp`, `env_ac_ainah_r2`, `nama_10_a64`, `naio_10_cp1700` |
| Prix d'achat : tableaux des emplois au prix d'acquisition et au prix de base, marges de commerce et de transport, impôts nets des subventions, colonne des marges du tableau des ressources | `naio_10_cp16`, `naio_10_cp1610`, `naio_10_cp1620`, `naio_10_cp1630`, `naio_10_cp15` |
| Vérité terrain : prix de l'électricité, émissions et production des centrales publiques, exportations d'acier | `nrg_pc_205`, `env_air_gge` (CRF 1.A.1.a), `nrg_bal_peh`, Comext `DS-045409` |
| Vérité terrain : intensité CO2 de l'acier brut, monde | worldsteel, World Steel in Figures [2024](https://worldsteel.org/wp-content/uploads/World-Steel-in-Figures-2024.pdf) et [2025](https://worldsteel.org/wp-content/uploads/World-Steel-in-Figures-2025.pdf) (`data/worldsteel_co2_intensity.csv`) |
| Contrôle : contenu amont en GES des produits français, tableau GES.501 | [SDES / Insee](https://www.statistiques.developpement-durable.gouv.fr/emissions-de-gaz-effet-de-serre-et-empreinte-carbone-de-la-france-une-baisse-significative-en-2023) |

Les émissions des pays hors UE sont les estimations fondées sur EDGAR produites par Eurostat
lui-même (note méthodologique « FIGARO - Greenhouse gas emission estimates »). Aucun modèle
d'émissions tiers n'est ajouté. L'Albanie, le Monténégro, la Macédoine du Nord et la Serbie sont
fusionnés dans le reste du monde, comme dans les comptes d'émissions publiés. Les requêtes et les
dates de mise à jour Eurostat de chaque extrait sont consignées dans `data/SOURCES.csv`.

### Éditions

Tableaux : édition 2026 (juin 2026). Émissions : publication Eurostat de janvier 2026, qui s'arrête
à 2023 ; **2023 est donc la dernière année complète**. Les comptes d'émissions dans l'air européens ne
dépendent pas de l'édition de FIGARO ; les estimations hors UE ont été ventilées par Eurostat avec
l'édition 2025. Le passage des tableaux de l'édition 2025 à l'édition 2026 modifie les facteurs
européens 2022-2023 de +0,3 % en médiane, 56 % d'entre eux restant à 5 % près et 9 % bougeant de
plus de 20 % (révisions des comptes nationaux).

### Année provisoire 2024

Les comptes d'émissions mondiaux s'arrêtent à 2023 : le total et le scope 3 amont ne peuvent pas
être calculés pour 2024. Les scopes 1 + 2 le peuvent : les comptes d'émissions dans l'air 2024 de
l'UE27 et de la Norvège ont été publiés en août 2026 (`env_ac_ainah_r2`) et le tableau 2024 existe.
Le scope 1 vaut comptes / production FIGARO ; le scope 2 utilise l'intensité directe 2024 des
fournisseurs d'électricité, de gaz et de vapeur, et l'intensité 2023 pour les fournisseurs situés
hors de ces 28 pays (0,7 % des scopes 1 + 2 en médiane). Les lignes 2024 seront remplacées par des
lignes complètes à la prochaine publication des comptes d'émissions par Eurostat.

## Contrôles

Rapports dans `results/<édition>/validation/`.

1. **Empreintes officielles d'Eurostat.** Appliqués à la demande finale FIGARO, les multiplicateurs
   redonnent l'empreinte publiée par Eurostat pour chaque pays : avec l'édition 2025, celle utilisée
   par Eurostat, ratio médian 1,0000, 96 % des 46 régions à 1 % près, écart maximal 2,1 %
   (`results/25ed`). Les tableaux de l'édition 2025 ne sont plus distribués, ce contrôle ne peut donc
   plus être relancé à partir de fichiers publics ; avec les tableaux 2026 l'accord n'est plus exact
   (35 à 52 % des régions à 1 % près).
2. **Scope 1.** Les émissions sont égales aux comptes d'émissions dans l'air pour 95 à 98 % des
   lignes ; l'intensité directe est à 5 % près de comptes / production des comptes nationaux pour
   96 à 100 % des lignes selon l'année, médiane 1,000.
3. **France, comparaison au tableau GES.501 du SDES et de l'Insee**, dont les valeurs sont celles
   que l'ADEME publie comme ratios monétaires :
   - ces facteurs : ratio médian de 0,82 à 0,88 selon l'année (2019 à 2023) ;
   - contenus importés FIGARO combinés au tableau entrées-sorties national français, ce qui
     approche la méthode du SDES : médiane de 0,94 à 0,96, 54 à 79 % des branches à 10 % près (2019 à 2022).

4. **Pays de demande.** Par rapport au facteur de production du même pays et du même produit : ratio
   médian de 1,04 à 1,05 selon l'année, 10 % des couples sous 0,93-0,95, 10 % au-dessus de
   1,37-1,45. Les plus forts pour les biens importés (textile 1,39, industries extractives 1,59 en 2023).
5. **Prix d'achat.** Valeur au prix de base + marges + taxes = prix d'achat pour 97,1 % des cellules
   où les quatre tableaux sont publiés (les autres sont écartées). Avec marges, le facteur au prix
   d'achat des biens vaut 0,91 à 0,92 fois le facteur au prix de base en médiane (10 % des lignes sous
   0,79-0,80), 0,98 pour les services ; le rebasage seul donne 0,85-0,86 pour les biens. Couverture par
   année et les deux tests de sensibilité dans le rapport.
6. **Variantes.** Achats finals par rapport aux achats des entreprises : ratio médian 1,00-1,01 pour les
   biens (10 % des couples au-dessus de 1,11-1,14), 0,99 pour les services. Rangs de la chaîne en
   médiane : émissions propres 10-11 %, rang 1 22-24 %, rang 2 21-22 %, rang 3 et au-delà 35-40 %.
   Forçage radiatif de l'aviation en 2023 : +51 % en médiane sur le transport aérien, +1 % en médiane sur
   les autres branches (déplacements professionnels), au plus +46 % (agences de voyage).
7. **Vérité terrain hors du modèle**, rapportée telle que mesurée (le modèle n'y est pas calé) :
   - **Électricité (D35)** par rapport à intensité du réseau / prix, soit les émissions d'inventaire des
     centrales publiques d'électricité et de chaleur (CRF 1.A.1.a) par kWh produit, divisées par le prix
     de l'électricité hors taxes pour les non-ménages, 2021 à 2023 (26 à 27 pays) : le facteur direct vaut
     0,55 à 0,59 fois cette valeur en médiane, le facteur total 0,97 à 1,15. La production de D35 couvre
     plus que l'électricité vendue aux entreprises : électricité échangée au sein de la branche, ventes aux ménages à des prix plus élevés, distribution de gaz et
     vapeur. Un facteur monétaire D35 est donc un mauvais substitut pour une facture d'électricité :
     utiliser un facteur par kWh.
   - **Métallurgie (C24)** par rapport à l'intensité CO2 mondiale de l'acier brut de worldsteel (1,91 et
     1,92 t par t en 2022 et 2023) divisée par la valeur unitaire des exportations d'acier de l'UE (Comext,
     SH 72 : 1 193 et 1 005 €/t) : le total C24 des 21 pays de l'UE au-dessus de 1 Md€ de production vaut
     0,58 et 0,46 fois cette valeur en médiane (de 539 à 1 661 kgCO2e/k€). Un écart attendu dans ce sens :
     C24 couvre aussi les métaux non ferreux et les fonderies, et le chiffre de worldsteel est une moyenne
     mondiale alors que les filières et les combustibles de la sidérurgie diffèrent selon les pays. Pour
     de l'acier acheté au poids, un facteur par tonne est préférable.

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
python build_purchaser_prices.py              # results/26ed/figaro_purchaser_prices_26ed.csv
python validate.py                            # results/26ed/validation/
python build_results.py                       # results/figaro_emission_factors_26ed.csv, figaro_demand_emission_factors_26ed.csv,
                                              # figaro_final_demand_emission_factors_26ed.csv,
                                              # figaro_supply_chain_details_26ed.csv, figaro_purchaser_price_factors_26ed.csv
```

Environ 5 minutes et 4 Go de mémoire une fois les tableaux téléchargés. Eurostat écrase ses jeux de
données en place : relancer `fetch_eurostat.py` plus tard peut renvoyer des données révisées ; les
extraits versionnés dans `data/` sont ceux des résultats publiés.

## Limites

- 64 branches, technologie moyenne de chaque branche dans chaque pays.
- Tableaux et estimations d'émissions proviennent de deux éditions consécutives de FIGARO.
- Les petits pays et les petites branches donnent des ratios instables malgré le seuil de 50 M€.
- Seule la distinction CO2 / autres gaz est possible sur toute la chaîne.
- Le scope 2 est en approche géographique et de premier rang ; D35 regroupe électricité, gaz et vapeur.
- Pays de demande : la répartition par origine est celle de FIGARO, qui sous-représente les biens
  importés par les branches françaises (voir plus haut) ; les facteurs de demande français des biens
  sont donc probablement un peu bas. Le reste du monde forme un seul bloc, avec un facteur par
  branche. Le mix d'achat d'une entreprise donnée peut s'écarter de la moyenne de son pays.
- Prix d'achat : moyennes nationales sur toutes les branches acheteuses, même partage des marges entre
  commerce et transport pour tous les produits, année la plus proche quand les matrices de passage ne
  sont pas annuelles. Les services de marge sont valorisés aux facteurs du pays acheteur (ils y sont
  produits).

## Licence et attribution

Code : MIT, voir `LICENSE`. Résultats et documentation : CC BY-SA 4.0 à partir de la version 2026.5
(versions 2026.1 à 2026.4 : CC BY 4.0). Détails dans `DATA_LICENSE.md` (en anglais), qui précise
aussi l'attribution due à Eurostat et au SDES / Insee pour les données d'entrée.

**La citation est obligatoire** pour tout usage des facteurs, à l'endroit où sont listées les sources
des données (rapport, méthodologie, documentation d'un produit ou d'une base) :

> FIGARO monetary emission factors, Ecodex (https://getecodex.com), version X, DOI 10.5281/zenodo.23157020,
> licence CC BY-SA 4.0. Computed from Eurostat data.

Une version adaptée des facteurs (valeurs modifiées, ou base construite sur une partie substantielle
d'entre eux) doit être partagée sous la même licence. Pour intégrer les facteurs dans un produit sans
cette obligation, ils sont disponibles via Ecodex Connect sous licence commerciale.

Pour citer : voir `CITATION.cff`. Archivé sur Zenodo : toutes versions https://doi.org/10.5281/zenodo.23157020, un DOI par version listé sur cette page.
