## 1. Validation et finalisation du catalogue haut-niveau

- [x] 1.1 Relire les deux specs (`scenarios-tarification-devis` et `scenarios-suivi-portefeuille`) et vérifier la cohérence des IDs de scénarios (format `<PERSONA>-TAR/SUV-NN`)
- [x] 1.2 Vérifier la couverture fonctionnelle : chaque étape clé du parcours tarification (sélection univers, saisie profil, tarif, comparaison, export devis) est couverte par au moins un scénario
- [x] 1.3 Vérifier la couverture fonctionnelle : chaque vue clé du suivi/portefeuille (liste dossiers, détail dossier, portefeuille actif, tableaux de bord, alertes échéances) est couverte
- [x] 1.4 Confirmer que chaque persona dispose d'au moins 2 scénarios simples et 1 scénario complexe par périmètre
- [x] 1.5 Identifier et documenter les tools MCP impliqués dans chaque scénario (moteur de tarification, vue portefeuille, suivi dossiers, tableaux de bord)

## 2. Rédaction détaillée des scénarios — Périmètre Tarification et devis

- [x] 2.1 Rédiger le contenu détaillé des interactions pour les scénarios simples de Mathieu (MAT-TAR-01, MAT-TAR-02) — variante idéale
- [x] 2.2 Rédiger le contenu détaillé du scénario complexe de Mathieu (MAT-TAR-03) — variante idéale
- [x] 2.3 Rédiger le contenu détaillé des scénarios simples de Christine (CHR-TAR-01, CHR-TAR-02) — variante idéale
- [x] 2.4 Rédiger le contenu détaillé du scénario complexe de Christine (CHR-TAR-03) — variante idéale
- [x] 2.5 Rédiger le contenu détaillé des scénarios simples d'Alexandre (ALE-TAR-01, ALE-TAR-02) — variante idéale
- [x] 2.6 Rédiger le contenu détaillé du scénario complexe d'Alexandre (ALE-TAR-03) — variante idéale
- [x] 2.7 Rédiger le contenu détaillé des scénarios simples d'Isabelle (ISA-TAR-01, ISA-TAR-02) — variante idéale
- [x] 2.8 Rédiger le contenu détaillé du scénario complexe d'Isabelle (ISA-TAR-03) — variante idéale
- [x] 2.9 Rédiger le contenu détaillé des scénarios simples de Karim (KAR-TAR-01, KAR-TAR-02) — variante idéale
- [x] 2.10 Rédiger le contenu détaillé du scénario complexe de Karim (KAR-TAR-03) — variante idéale
- [x] 2.11 Rédiger le contenu détaillé des scénarios simples de Nathalie (NAT-TAR-01, NAT-TAR-02) — variante idéale
- [x] 2.12 Rédiger le contenu détaillé du scénario complexe de Nathalie (NAT-TAR-03) — variante idéale

## 3. Rédaction détaillée des scénarios — Périmètre Suivi des dossiers et portefeuille

- [x] 3.1 Rédiger le contenu détaillé des scénarios simples de Mathieu (MAT-SUV-01, MAT-SUV-02) — variante idéale
- [x] 3.2 Rédiger le contenu détaillé du scénario complexe de Mathieu (MAT-SUV-03) — variante idéale
- [x] 3.3 Rédiger le contenu détaillé des scénarios simples de Christine (CHR-SUV-01, CHR-SUV-02) — variante idéale
- [x] 3.4 Rédiger le contenu détaillé du scénario complexe de Christine (CHR-SUV-03) — variante idéale
- [x] 3.5 Rédiger le contenu détaillé des scénarios simples d'Alexandre (ALE-SUV-01, ALE-SUV-02) — variante idéale
- [x] 3.6 Rédiger le contenu détaillé du scénario complexe d'Alexandre (ALE-SUV-03) — variante idéale
- [x] 3.7 Rédiger le contenu détaillé des scénarios simples d'Isabelle (ISA-SUV-01, ISA-SUV-02) — variante idéale
- [x] 3.8 Rédiger le contenu détaillé du scénario complexe d'Isabelle (ISA-SUV-03) — variante idéale
- [x] 3.9 Rédiger le contenu détaillé des scénarios simples de Karim (KAR-SUV-01, KAR-SUV-02) — variante idéale
- [x] 3.10 Rédiger le contenu détaillé du scénario complexe de Karim (KAR-SUV-03) — variante idéale
- [x] 3.11 Rédiger le contenu détaillé des scénarios simples de Nathalie (NAT-SUV-01, NAT-SUV-02) — variante idéale
- [x] 3.12 Rédiger le contenu détaillé du scénario complexe de Nathalie (NAT-SUV-03) — variante idéale

## 4. Génération des variantes court (réaliste) et adversarial

- [x] 4.1 Générer les variantes « court/réaliste » pour chaque scénario simple du périmètre tarification (langage oral, fautes de frappe, contexte partiel)
- [x] 4.2 Générer les variantes « court/réaliste » pour chaque scénario complexe du périmètre tarification
- [x] 4.3 Générer les variantes « court/réaliste » pour chaque scénario simple du périmètre suivi/portefeuille
- [x] 4.4 Générer les variantes « court/réaliste » pour chaque scénario complexe du périmètre suivi/portefeuille
- [x] 4.5 Générer les variantes « adversarial » pour un sous-ensemble représentatif de scénarios (2 par persona minimum) — prompt injection, hors-scope, demandes ambiguës
- [x] 4.6 Valider que les variantes adversariales couvrent les deux périmètres et plusieurs personas

## 5. Construction des datasets JSONL

- [x] 5.1 Structurer les scénarios tarification-devis en fichiers JSONL dans `runner/datasets/` (format : id, scenario_family, domain, input, expected, expected_matches)
- [x] 5.2 Structurer les scénarios suivi-portefeuille en fichiers JSONL dans `runner/datasets/`
- [x] 5.3 Vérifier la cohérence des champs `scenario_family` (ideal, court, adversarial) et `domain` sur l'ensemble des entrées
- [x] 5.4 Ajouter les métadonnées de persona (`persona_id`) dans chaque entrée JSONL pour permettre le filtrage par persona lors des runs

## 6. Identification et bouchonnage des tools MCP

- [x] 6.1 Lister tous les tools MCP distincts identifiés dans les scénarios (tarification, comparaison multi-offres, suivi dossiers, portefeuille, tableaux de bord)
- [x] 6.2 Définir les interfaces (inputs/outputs) de chaque tool MCP identifié
- [x] 6.3 Implémenter les bouchons MCP pour les tools du périmètre tarification/devis
- [x] 6.4 Implémenter les bouchons MCP pour les tools du périmètre suivi/portefeuille
- [x] 6.5 Tester les bouchons MCP avec un sous-ensemble de scénarios avant de lancer les runs d'évaluation complets
