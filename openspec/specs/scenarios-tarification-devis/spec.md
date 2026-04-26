## ADDED Requirements

### Requirement: Structure du catalogue — Tarification et devis
Le catalogue de scénarios sur le périmètre « Parcours de tarification et de devis » SHALL être organisé par persona. Pour chaque persona, il SHALL contenir au minimum 2 scénarios simples et 1 scénario complexe. Chaque scénario SHALL préciser : ID, titre, complexité, résumé, et tools MCP impliqués.

#### Scenario: Accès au catalogue par persona
- **WHEN** un évaluateur cherche des scénarios pour une persona spécifique
- **THEN** le catalogue SHALL présenter tous les scénarios de cette persona regroupés et identifiables par leur préfixe d'ID

#### Scenario: Cohérence de la couverture fonctionnelle
- **WHEN** on examine l'ensemble du catalogue tarification-devis
- **THEN** chaque étape clé du parcours (sélection univers, saisie profil, obtention tarif, comparaison, export devis) SHALL être couverte par au moins un scénario sur l'ensemble des personas

---

### Requirement: Scénarios Mathieu — Tarification emprunteur
Mathieu est courtier emprunteur spécialisé, utilisateur quotidien intensif. Le catalogue SHALL inclure des scénarios couvrant ses besoins principaux sur la tarification et le devis emprunteur, incluant les profils standards et aggravés.

#### Scenario: MAT-TAR-01 — Tarification emprunteur standard Lemoine (Simple)
- **WHEN** Mathieu demande un tarif pour un client standard (35 ans, prêt immobilier 200K€, 20 ans, pas de risque médical particulier) et veut savoir si le dossier relève de Lemoine
- **THEN** le chatbot SHALL identifier l'éligibilité Lemoine, lancer une comparaison multi-offres jRensure, et présenter les tarifs disponibles

#### Scenario: MAT-TAR-02 — Identification pièces justificatives par gamme (Simple)
- **WHEN** Mathieu demande quelles pièces justificatives sont requises pour une gamme emprunteur spécifique avant de soumettre un devis
- **THEN** le chatbot SHALL lister les pièces requises pour la gamme concernée sans que Mathieu ait à naviguer dans la documentation

#### Scenario: MAT-TAR-03 — Profil à risques aggravés, multi-offres Lemoine vs hors-Lemoine (Complexe)
- **WHEN** Mathieu a un client TNS avec antécédent médical, souhaitant assurer un prêt immobilier ET un prêt professionnel simultanément, et doit comparer les options Lemoine (si éligible) et hors-Lemoine
- **THEN** le chatbot SHALL guider le diagnostic d'éligibilité Lemoine par prêt, identifier les gammes disponibles pour profils aggravés, et synthétiser les options de comparaison multi-offres pour les deux prêts

---

### Requirement: Scénarios Christine — Tarification multi-univers
Christine est courtière généraliste. Le catalogue SHALL inclure des scénarios couvrant sa capacité à tarifier sur plusieurs univers dans une même session, incluant des univers peu fréquents pour elle.

#### Scenario: CHR-TAR-01 — Tarification santé individuelle salarié (Simple)
- **WHEN** Christine demande un devis santé individuelle pour un salarié de 45 ans avec conjoint et deux enfants
- **THEN** le chatbot SHALL demander les informations complémentaires nécessaires (régime social, niveau souhaité) et initier le parcours de tarification santé

#### Scenario: CHR-TAR-02 — Devis GAV pour retraité (Simple)
- **WHEN** Christine, peu experte sur le GAV, demande comment tarifier une GAV pour un client retraité de 68 ans
- **THEN** le chatbot SHALL expliquer les données à saisir, les garanties disponibles et guider vers le parcours de tarification GAV

#### Scenario: CHR-TAR-03 — Client TNS multi-produits : dévis croisés santé + prévoyance + emprunteur (Complexe)
- **WHEN** Christine a un nouveau client TNS artisan (42 ans) qui souhaite être équipé sur santé, prévoyance Madelin et emprunteur pro, et demande quel ordre de parcours adopter et quelles données collecter en une seule fois
- **THEN** le chatbot SHALL proposer une organisation des trois parcours de devis (ordre logique, données communes à collecter une seule fois), signaler les interdépendances (ex. profession à risque impacte tarification GAV et emprunteur) et identifier les comparateurs disponibles par univers

---

### Requirement: Scénarios Alexandre — Tarification via API
Alexandre est néo-courtier digital. Le catalogue SHALL inclure des scénarios couvrant l'usage technique de l'API de tarification et la génération automatisée de devis conformes DDA.

#### Scenario: ALE-TAR-01 — Format d'entrée API tarification emprunteur (Simple)
- **WHEN** Alexandre demande le format des paramètres d'entrée pour l'API de tarification emprunteur (type de prêt, montant, durée, profil)
- **THEN** le chatbot SHALL retourner la structure exacte des paramètres, les types attendus et les valeurs admissibles

#### Scenario: ALE-TAR-02 — Codes erreur du moteur de tarification (Simple)
- **WHEN** Alexandre reçoit un code erreur lors d'un appel à l'API de tarification et demande sa signification
- **THEN** le chatbot SHALL identifier l'erreur, en expliquer la cause et proposer les corrections possibles

#### Scenario: ALE-TAR-03 — Pipeline automatisé de devis en volume avec conformité DDA (Complexe)
- **WHEN** Alexandre veut automatiser la génération de 100+ devis DDA par jour via l'API, en gérant les erreurs de tarification, les cas hors-éligibilité et la génération conforme des PDF
- **THEN** le chatbot SHALL décrire les contraintes DDA sur la génération automatique, les limites de l'API (SLA, rate limiting), les cas nécessitant une intervention manuelle, et les logs recommandés pour la traçabilité

---

### Requirement: Scénarios Isabelle — Tarification profils patrimoniaux complexes
Isabelle est CGP. Le catalogue SHALL inclure des scénarios couvrant les profils atypiques à hauts capitaux assurés et les gammes non-Lemoine pour prêts professionnels.

#### Scenario: ISA-TAR-01 — Comparaison Lemoine vs hors-Lemoine pour investissement locatif (Simple)
- **WHEN** Isabelle demande si un prêt pour investissement locatif de 500K€ pour un client de 50 ans relève de Lemoine ou non, et quelles sont les implications pratiques
- **THEN** le chatbot SHALL identifier que l'investissement locatif est hors-Lemoine, expliquer les conséquences (questionnaire médical complet, conditions d'âge) et orienter vers les gammes hors-Lemoine disponibles

#### Scenario: ISA-TAR-02 — Conditions de souscription pour capitaux assurés élevés (Simple)
- **WHEN** Isabelle demande les conditions de souscription pour un capital assuré de 2M€ sur un prêt professionnel d'un dirigeant de 55 ans
- **THEN** le chatbot SHALL préciser si des gammes couvrent ce niveau de capital, les conditions médicales requises et les délais de sélection médicale associés

#### Scenario: ISA-TAR-03 — Montage multi-prêts avec modularité avancée (Complexe)
- **WHEN** Isabelle a un client dirigeant avec un prêt pro (1,5M€) et un prêt immobilier personnel (600K€), souhaitant des options de modularité différentes pour chacun (rente vs capital IPT, quotités personnalisées), et demande comment construire les deux devis en tenant compte des profils médicaux
- **THEN** le chatbot SHALL guider la construction des deux devis en parallèle, identifier les options de modularité disponibles par gamme, et synthétiser les incompatibilités potentielles entre les deux montages

---

### Requirement: Scénarios Karim — Tarification TNS et professions libérales
Karim est courtier spécialisé TNS. Le catalogue SHALL inclure des scénarios couvrant les gammes TNS, la fiscalité Madelin et les professions à risques.

#### Scenario: KAR-TAR-01 — Tarif santé TNS pour profession libérale (Simple)
- **WHEN** Karim demande un tarif santé individuelle pour un médecin libéral de 48 ans (TNS) avec des garanties dentaires et optiques renforcées
- **THEN** le chatbot SHALL identifier les gammes TNS disponibles, lancer le parcours de tarification santé TNS et présenter les options adaptées au profil

#### Scenario: KAR-TAR-02 — Plafonds déductibilité Madelin pour prévoyance (Simple)
- **WHEN** Karim demande quels sont les plafonds de déductibilité Madelin pour un contrat prévoyance d'un artisan avec un revenu imposable de 60K€
- **THEN** le chatbot SHALL calculer ou expliquer les règles de plafonnement Madelin applicables et orienter vers le simulateur fiscal si disponible

#### Scenario: KAR-TAR-03 — Portefeuille TNS multi-produits à renouveler : devis groupés (Complexe)
- **WHEN** Karim doit renouveler simultanément pour un client artisan BTP (45 ans) les contrats santé TNS, prévoyance Madelin, GAV (profession à risque BTP) et emprunteur pro, et veut optimiser le parcours de devis pour minimiser les ressaisies
- **THEN** le chatbot SHALL identifier les données communes entre les univers, signaler les spécificités BTP (risque aggravé GAV, questionnaire médical emprunteur pro), et proposer un parcours de devis ordonné minimisant les ressaisies

---

### Requirement: Scénarios Nathalie — Tarification santé collective et prévoyance d'entreprise
Nathalie est courtière santé collective. Le catalogue SHALL inclure des scénarios couvrant la tarification collective avec vérification de conformité CCN et gestion des appels d'offres.

#### Scenario: NAT-TAR-01 — Tarification santé collective PME avec CCN (Simple)
- **WHEN** Nathalie demande une tarification santé collective pour une PME de 25 salariés soumise à la CCN de la métallurgie
- **THEN** le chatbot SHALL identifier les obligations minimales de la CCN métallurgie, lancer le parcours de tarification santé collective et signaler les garanties obligatoires à intégrer

#### Scenario: NAT-TAR-02 — Documents DDA requis pour un devis collectif (Simple)
- **WHEN** Nathalie demande quels documents DDA sont obligatoires pour remettre un devis santé collective à une entreprise cliente
- **THEN** le chatbot SHALL lister les obligations DDA spécifiques aux contrats collectifs (IPID, fiche conseil, DER) et préciser les conditions de remise

#### Scenario: NAT-TAR-03 — Appel d'offres multi-niveaux de garanties avec conformité ANI et CCN (Complexe)
- **WHEN** Nathalie répond à un appel d'offres pour une PME de 50 salariés (CCN HCR), veut comparer 3 niveaux de garanties santé + prévoyance collective, et doit vérifier la conformité ANI et CCN pour chaque option avant de remettre un devis
- **THEN** le chatbot SHALL guider la vérification de conformité ANI/CCN HCR, faciliter la comparaison des niveaux de garanties disponibles, et aider à constituer le dossier d'appel d'offres avec les documents DDA requis

---

## MCP Tools Mapping — Périmètre Tarification et devis

> Cartographie des tools MCP impliqués par scénario. Référence pour l'identification et l'implémentation des bouchons.

| Scénario | Tools MCP impliqués |
|---|---|
| MAT-TAR-01 | `check_lemoine_eligibility`, `compare_offres` |
| MAT-TAR-02 | `get_pieces_justificatives` |
| MAT-TAR-03 | `check_lemoine_eligibility`, `compare_offres`, `compute_tarif` |
| CHR-TAR-01 | `compute_tarif` |
| CHR-TAR-02 | `compute_tarif` |
| CHR-TAR-03 | `compute_tarif`, `compare_offres` |
| ALE-TAR-01 | `get_api_tarification_schema` |
| ALE-TAR-02 | `get_api_tarification_schema` |
| ALE-TAR-03 | `get_api_tarification_schema`, `export_devis` |
| ISA-TAR-01 | `check_lemoine_eligibility`, `compare_offres` |
| ISA-TAR-02 | `compute_tarif` |
| ISA-TAR-03 | `compute_tarif`, `compare_offres` |
| KAR-TAR-01 | `compute_tarif` |
| KAR-TAR-02 | `get_madelin_plafonds` |
| KAR-TAR-03 | `compute_tarif`, `compare_offres` |
| NAT-TAR-01 | `compute_tarif`, `check_ccn_compliance` |
| NAT-TAR-02 | `export_devis` |
| NAT-TAR-03 | `compute_tarif`, `compare_offres`, `check_ccn_compliance`, `export_devis` |

### Tools catalogue

| Tool | Description |
|---|---|
| `check_lemoine_eligibility` | Vérifie l'éligibilité Loi Lemoine d'un prêt (type, capital, âge au terme) |
| `compare_offres` | Lance une comparaison multi-offres sur un univers donné et retourne le tableau comparatif |
| `compute_tarif` | Calcule le tarif pour un profil client et un produit donnés |
| `get_pieces_justificatives` | Retourne la liste des pièces justificatives requises par gamme/produit |
| `export_devis` | Génère et retourne le PDF du devis conforme DDA |
| `get_api_tarification_schema` | Retourne le schéma de l'API de tarification (paramètres, types, codes erreur) |
| `get_madelin_plafonds` | Calcule les plafonds de déductibilité Madelin selon le revenu et le type de contrat |
| `check_ccn_compliance` | Vérifie la conformité des garanties collectives avec une CCN donnée |
