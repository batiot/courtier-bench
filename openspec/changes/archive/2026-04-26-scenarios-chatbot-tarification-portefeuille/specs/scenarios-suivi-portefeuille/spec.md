## ADDED Requirements

### Requirement: Structure du catalogue — Suivi des dossiers et portefeuille
Le catalogue de scénarios sur le périmètre « Suivi des dossiers et gestion du portefeuille » SHALL être organisé par persona. Pour chaque persona, il SHALL contenir au minimum 2 scénarios simples et 1 scénario complexe. Chaque scénario SHALL préciser : ID, titre, complexité, résumé, et tools MCP impliqués.

#### Scenario: Accès au catalogue par persona
- **WHEN** un évaluateur cherche des scénarios de suivi pour une persona spécifique
- **THEN** le catalogue SHALL présenter tous les scénarios de cette persona regroupés et identifiables par leur préfixe d'ID

#### Scenario: Cohérence de la couverture fonctionnelle
- **WHEN** on examine l'ensemble du catalogue suivi-portefeuille
- **THEN** chaque vue clé du portail (liste dossiers, détail dossier, portefeuille actif, tableaux de bord, alertes échéances) SHALL être couverte par au moins un scénario sur l'ensemble des personas

---

### Requirement: Scénarios Mathieu — Suivi dossiers emprunteur
Mathieu est courtier emprunteur spécialisé avec un volume élevé de dossiers. Le catalogue SHALL inclure des scénarios couvrant le suivi en temps réel des statuts, les dossiers bloqués et les tableaux de bord de production.

#### Scenario: MAT-SUV-01 — Vérification du statut d'un dossier soumis (Simple)
- **WHEN** Mathieu demande où en est un dossier emprunteur soumis la veille, en donnant la référence client
- **THEN** le chatbot SHALL retourner le statut actuel du dossier, la date de dernière mise à jour et indiquer si une action est attendue de sa part

#### Scenario: MAT-SUV-02 — Téléchargement de l'attestation après acceptation (Simple)
- **WHEN** Mathieu demande comment récupérer l'attestation d'assurance et le numéro de police d'un dossier accepté
- **THEN** le chatbot SHALL guider vers le téléchargement des documents contractuels (attestation, conditions particulières, tableau des garanties) depuis le portail

#### Scenario: MAT-SUV-03 — Tableau de bord mensuel : production, taux de transformation, dossiers bloqués (Complexe)
- **WHEN** Mathieu veut un bilan mensuel de son activité emprunteur : nombre de devis générés, taux de transformation, volume de dossiers par statut (soumis, en attente de pièces, refusés), et identifier les actions prioritaires pour débloquer les dossiers en attente
- **THEN** le chatbot SHALL orienter vers le tableau de bord de production, expliquer comment interpréter les indicateurs, identifier les dossiers « en attente de pièces » comme priorité, et guider les actions de relance

---

### Requirement: Scénarios Christine — Suivi portefeuille multi-univers
Christine gère un portefeuille tous univers. Le catalogue SHALL inclure des scénarios couvrant la vue consolidée, les alertes d'échéance et la recherche d'historique.

#### Scenario: CHR-SUV-01 — Contrats arrivant à échéance dans les 30 jours (Simple)
- **WHEN** Christine demande quels contrats arrivent à échéance dans les 30 prochains jours et pour lesquels elle doit anticiper un renouvellement
- **THEN** le chatbot SHALL lister les contrats concernés avec leur univers, leur statut et les actions recommandées avant l'échéance

#### Scenario: CHR-SUV-02 — Retrouver un devis ancien (Simple)
- **WHEN** Christine cherche un devis émis il y a 3 mois pour un client dont elle ne se souvient que du prénom
- **THEN** le chatbot SHALL guider l'utilisation des filtres de recherche du portail (par période, par univers) pour retrouver le devis

#### Scenario: CHR-SUV-03 — Vue portefeuille consolidée multi-univers : priorisation des actions (Complexe)
- **WHEN** Christine veut une vue d'ensemble de son portefeuille actif (tous univers confondus) en début de semaine, identifier les relances prioritaires (renouvellements proches, dossiers en attente de pièces, commissions à vérifier) et organiser ses actions de la semaine
- **THEN** le chatbot SHALL combiner les vues portefeuille et suivi dossiers, filtrer par urgence (échéances < 30 jours, statuts bloquants), et proposer un plan d'actions priorisé sur les différents univers

---

### Requirement: Scénarios Alexandre — Suivi automatisé via API
Alexandre utilise les APIs pour un suivi en masse. Le catalogue SHALL inclure des scénarios couvrant la récupération programmatique des statuts, les webhooks/polling et la gestion des SLA.

#### Scenario: ALE-SUV-01 — API de récupération du statut de souscription (Simple)
- **WHEN** Alexandre demande quelle API utiliser pour récupérer le statut d'un dossier de souscription en temps réel et dans quel format est retourné le statut
- **THEN** le chatbot SHALL décrire le endpoint de statut, le format de réponse (codes statut, champs disponibles) et les cas de non-disponibilité

#### Scenario: ALE-SUV-02 — Configuration du polling sur les événements de statut (Simple)
- **WHEN** Alexandre demande comment implémenter un système de polling sur les changements de statut de souscription en l'absence de webhooks natifs
- **THEN** le chatbot SHALL expliquer la fréquence recommandée, les bonnes pratiques pour éviter le rate limiting, et les événements clés à surveiller (soumis → accepté, soumis → en attente de pièces, etc.)

#### Scenario: ALE-SUV-03 — Gestion en masse des dossiers bloqués : automatisation et SLA (Complexe)
- **WHEN** Alexandre détecte via son système que 50 dossiers sont en statut « en attente de pièces » depuis plus de 48h et veut automatiser les relances, mesurer le respect des SLA de traitement et escalader les cas critiques
- **THEN** le chatbot SHALL expliquer les actions disponibles via le portail/API pour les dossiers bloqués, les SLA de traitement attendus par statut, les modalités d'escalade (support technique) et les données de logs disponibles pour l'audit

---

### Requirement: Scénarios Isabelle — Suivi dossiers patrimoniaux complexes
Isabelle gère des dossiers à valeur élevée avec plusieurs contrats par client. Le catalogue SHALL inclure des scénarios couvrant le suivi individuel de dossiers complexes et la vue consolidée par client.

#### Scenario: ISA-SUV-01 — Suivi d'un dossier en sélection médicale (Simple)
- **WHEN** Isabelle demande où en est un dossier emprunteur pro soumis depuis 10 jours qui semble bloqué en sélection médicale
- **THEN** le chatbot SHALL indiquer comment identifier ce statut dans le portail, les délais habituels de sélection médicale pour les profils complexes, et les actions possibles (relance, documents complémentaires)

#### Scenario: ISA-SUV-02 — Accès aux documents contractuels d'un contrat signé (Simple)
- **WHEN** Isabelle cherche à consulter les conditions particulières d'un contrat prévoyance signé il y a 6 mois pour un client dirigeant
- **THEN** le chatbot SHALL guider la navigation vers les documents contractuels dans la vue portefeuille et expliquer les documents disponibles (conditions particulières, tableau des garanties)

#### Scenario: ISA-SUV-03 — Vue client consolidée multi-contrats : suivi et échéances (Complexe)
- **WHEN** Isabelle prépare un rendez-vous annuel avec un client ayant 3 contrats actifs (emprunteur pro, prévoyance Madelin, santé TNS) et veut une vue consolidée de son portefeuille : statuts, prochaines échéances, modifications de garanties à envisager
- **THEN** le chatbot SHALL agréger les informations des trois contrats depuis le portail, identifier les échéances et les points d'attention (évolution de situation professionnelle, plafonds Madelin à vérifier), et préparer un récapitulatif pour le rendez-vous

---

### Requirement: Scénarios Karim — Suivi renouvellements TNS
Karim gère un portefeuille TNS avec des renouvellements annuels complexes. Le catalogue SHALL inclure des scénarios couvrant le suivi des contrats Madelin, les modifications de garanties et les alertes de renouvellement.

#### Scenario: KAR-SUV-01 — Vérification du statut d'un dossier prévoyance TNS (Simple)
- **WHEN** Karim vérifie si un dossier prévoyance TNS soumis pour un nouveau client est bien en cours de traitement ou encore en attente
- **THEN** le chatbot SHALL retourner le statut du dossier, identifier si des pièces sont manquantes (questionnaire médical, justificatif de revenus) et guider l'action corrective

#### Scenario: KAR-SUV-02 — Modification des garanties d'un contrat santé TNS actif (Simple)
- **WHEN** Karim veut modifier le niveau de garanties d'un contrat santé TNS actif suite à un changement de situation d'un client (mariage, naissance)
- **THEN** le chatbot SHALL expliquer la procédure de modification depuis le portail, les délais de prise d'effet et les documents éventuellement requis

#### Scenario: KAR-SUV-03 — Renouvellement annuel multi-contrats TNS : alertes et actions groupées (Complexe)
- **WHEN** Karim approche de la période de renouvellement annuel pour un portefeuille de 15 clients TNS avec des contrats santé, prévoyance et emprunteur pro arrivant à échéance sur les 60 prochains jours, et veut prioriser les actions, anticiper les hausses de tarifs et gérer les résiliations éventuelles
- **THEN** le chatbot SHALL combiner les alertes d'échéances du portail, identifier les contrats nécessitant une action active vs automatiquement reconduits, expliquer les règles de résiliation (Lemoine pour emprunteur, délais de préavis), et proposer un plan de campagne de renouvellement priorisé

---

### Requirement: Scénarios Nathalie — Suivi contrats collectifs et gestion d'entreprise
Nathalie gère des contrats collectifs avec des événements RH fréquents. Le catalogue SHALL inclure des scénarios couvrant la gestion des effectifs, la portabilité et les renouvellements collectifs.

#### Scenario: NAT-SUV-01 — Statut d'un dossier santé collective en cours de traitement (Simple)
- **WHEN** Nathalie demande où en est un dossier santé collective pour une PME cliente soumis il y a une semaine
- **THEN** le chatbot SHALL retourner le statut, identifier si des documents complémentaires sont attendus (accord collectif, liste du personnel) et indiquer les délais habituels

#### Scenario: NAT-SUV-02 — Gestion de la sortie d'un salarié : portabilité Loi Evin (Simple)
- **WHEN** Nathalie doit gérer la sortie d'un salarié d'une PME cliente et veut savoir comment traiter la portabilité depuis le portail et quelles sont les obligations au titre de la Loi Evin
- **THEN** le chatbot SHALL expliquer les règles de maintien de garanties (durée, conditions), la procédure de déclaration depuis le portail, et les documents à remettre au salarié sortant

#### Scenario: NAT-SUV-03 — Renouvellement annuel contrat collectif : mise à jour effectifs, garanties, conformité CCN (Complexe)
- **WHEN** Nathalie prépare le renouvellement annuel d'un contrat santé collective d'une PME de 40 salariés (CCN BTP) avec des changements de garanties demandés par l'entreprise, une évolution des effectifs (+5 salariés) et un besoin de vérification de la conformité CCN BTP actualisée avant signature
- **THEN** le chatbot SHALL guider la mise à jour des effectifs dans le portail, vérifier la conformité des nouvelles garanties avec la CCN BTP, identifier les documents de formalisation requis (avenant, nouvelle notice) et accompagner le processus jusqu'à la signature électronique du renouvellement

---

## MCP Tools Mapping — Périmètre Suivi des dossiers et portefeuille

> Cartographie des tools MCP impliqués par scénario. Référence pour l'identification et l'implémentation des bouchons.

| Scénario | Tools MCP impliqués |
|---|---|
| MAT-SUV-01 | `get_dossier_status` |
| MAT-SUV-02 | `get_documents_contractuels` |
| MAT-SUV-03 | `get_tableau_de_bord`, `get_dossier_status` |
| CHR-SUV-01 | `get_echeances_alertes` |
| CHR-SUV-02 | `get_portefeuille` |
| CHR-SUV-03 | `get_portefeuille`, `get_echeances_alertes`, `get_dossier_status` |
| ALE-SUV-01 | `get_api_statut_schema` |
| ALE-SUV-02 | `get_api_statut_schema` |
| ALE-SUV-03 | `get_dossier_status`, `get_tableau_de_bord` |
| ISA-SUV-01 | `get_dossier_status` |
| ISA-SUV-02 | `get_documents_contractuels` |
| ISA-SUV-03 | `get_portefeuille`, `get_echeances_alertes`, `get_documents_contractuels` |
| KAR-SUV-01 | `get_dossier_status` |
| KAR-SUV-02 | `modifier_contrat` |
| KAR-SUV-03 | `get_echeances_alertes`, `get_portefeuille`, `get_dossier_status` |
| NAT-SUV-01 | `get_dossier_status` |
| NAT-SUV-02 | `modifier_contrat` |
| NAT-SUV-03 | `get_portefeuille`, `modifier_contrat`, `check_ccn_compliance`, `get_documents_contractuels` |

### Tools catalogue

| Tool | Description |
|---|---|
| `get_dossier_status` | Retourne le statut d'un dossier soumis (statut, date MAJ, actions en attente) |
| `get_portefeuille` | Retourne la vue portefeuille active avec filtres (univers, statut, persona) |
| `get_echeances_alertes` | Retourne les contrats arrivant à échéance sur une période donnée |
| `get_tableau_de_bord` | Retourne le tableau de bord de production (KPIs, dossiers par statut, volume) |
| `get_documents_contractuels` | Retourne les documents contractuels téléchargeables d'un contrat actif |
| `modifier_contrat` | Initie une modification de garanties sur un contrat actif |
| `get_api_statut_schema` | Retourne le schéma du endpoint de statut API (format, codes, SLA) |
| `check_ccn_compliance` | Vérifie la conformité des garanties collectives avec une CCN donnée |
