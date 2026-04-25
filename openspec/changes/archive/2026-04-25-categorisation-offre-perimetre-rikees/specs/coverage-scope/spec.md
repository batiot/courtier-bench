## ADDED Requirements

### Requirement: Périmètre de couverture par ligne de produit
Le système SHALL exposer pour chaque ligne de produit les garanties couvertes, les profils éligibles, les conditions d'âge et les éventuels plafonds ou dispositifs réglementaires applicables.

#### Scenario: Couverture assurance emprunteur — profils éligibles
- **WHEN** le tool `get_coverage_scope` est appelé avec `product_line = "assurance-emprunteur"`
- **THEN** le système retourne les profils éligibles (primo-accédants, seniors, risques médicaux aggravés, professions à risques) et les types de prêts couverts (immobilier, personnel, professionnel, investissement locatif)

#### Scenario: Dispositifs réglementaires applicables
- **WHEN** Genia reçoit "L'offre emprunteur Rikees inclut-elle des contrats conformes à la loi Lemoine ?"
- **THEN** Genia confirme l'existence de dispositifs Lemoine et non-Lemoine dans la gamme et précise les modalités de modularité

#### Scenario: Couverture prévoyance individuelle
- **WHEN** le tool `get_coverage_scope` est appelé avec `product_line = "prevoyance-individuelle"`
- **THEN** le système retourne les garanties (décès, invalidité, arrêt de travail, perte d'emploi, obsèques) et identifie Rikees France comme gestionnaire opérationnel

### Requirement: Exclusions et limites de souscription
Le système SHALL documenter les exclusions de garantie et les limites de souscription (conditions d'âge, capitaux assurés, restrictions médicales) pour chaque ligne de produit.

#### Scenario: Plafonds de capitaux assurés
- **WHEN** Genia reçoit "Y a-t-il un plafond sur les capitaux assurés en emprunteur ?"
- **THEN** Genia indique que certaines offres proposent des capitaux assurés illimités et précise les conditions associées

#### Scenario: Question sur une exclusion inexistante
- **WHEN** Genia reçoit une question sur une exclusion qui n'est pas documentée dans la knowledge base
- **THEN** Genia indique qu'elle ne dispose pas de cette information et ne fabrique pas d'exclusion

### Requirement: Adéquation offre / profil client
Le système SHALL permettre de déterminer quelle ligne de produit est adaptée à un profil client donné (particulier, TNS, professionnel, senior, profil à risque aggravé).

#### Scenario: Orientation profil TNS
- **WHEN** Genia reçoit "Quels produits Rikees sont adaptés aux travailleurs non-salariés ?"
- **THEN** Genia cite la prévoyance professionnelle et la complémentaire santé TNS, en précisant les entités concernées

#### Scenario: Profil à risque médical aggravé
- **WHEN** Genia reçoit "Un client avec des antécédents médicaux peut-il souscrire une assurance emprunteur via Rikees ?"
- **THEN** Genia confirme l'existence d'offres dédiées aux risques médicaux aggravés dans la gamme emprunteur
