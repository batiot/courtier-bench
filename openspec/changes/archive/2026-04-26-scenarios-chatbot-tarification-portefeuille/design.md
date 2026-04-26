## Context

Le projet courtier-bench vise à construire un benchmark d'évaluation pour le chatbot Genia, déployé dans l'Espace partenaire Rikees Sol. Pour être représentatif, le benchmark doit couvrir les interactions réelles des 6 personas courtiers identifiés, en se concentrant sur les deux périmètres fonctionnels les plus fréquents : la tarification/devis et le suivi des dossiers/portefeuille.

Cette phase de conception ne produit pas de code : elle définit la structure et le contenu haut niveau du catalogue de scénarios, qui servira de base pour la génération détaillée des conversations et la construction des datasets JSONL.

Parties prenantes : évaluateurs du benchmark, rédacteurs des conversations, responsables de l'identification des tools MCP.

## Goals / Non-Goals

**Goals:**

- Définir une structure cohérente pour organiser les scénarios d'interaction par persona et par périmètre
- Couvrir les deux périmètres fonctionnels : tarification/devis et suivi/portefeuille
- Pour chaque persona, avoir au minimum 2 scénarios simples et 1 scénario complexe par périmètre
- Classifier les scénarios selon la famille d'évaluation (idéal, court/réaliste, adversarial)
- Assurer la cohérence et la couverture fonctionnelle des périmètres (pas de zone d'ombre)
- Identifier les tools MCP impliqués dans chaque scénario

**Non-Goals:**

- Rédiger le contenu détaillé des échanges chatbot (phase ultérieure)
- Implémenter les tools MCP ou les datasets JSONL (phases suivantes)
- Couvrir les périmètres hors scope : souscription, sinistres, conformité documentaire

## Decisions

### Organisation par périmètre puis par persona

**Décision** : deux specs séparées, une par périmètre fonctionnel, chacune organisant les scénarios par persona.

**Rationale** : un courtier navigue d'abord par périmètre fonctionnel sur le portail. Organiser par périmètre facilite la génération de datasets ciblés et l'identification des tools MCP propres à chaque parcours. Une organisation par persona uniquement diluerait la cohérence fonctionnelle.

**Alternative écartée** : un seul catalogue plat — rejeté car il rend difficile la maintenance et le ciblage des évaluations.

---

### Classification des scénarios : simple vs complexe

**Décision** :
- **Simple** : une seule interaction, un seul périmètre fonctionnel, intention non ambiguë, contexte suffisant
- **Complexe** : au moins deux de ces critères — plusieurs étapes, plusieurs périmètres, contexte partiel, ou profil atypique nécessitant une logique conditionnelle

**Rationale** : cette classification guide directement la famille d'évaluation et le niveau de grading requis (LLM-as-judge simple vs chaîne d'évaluation multi-critères).

---

### Familles de scénarios (idéal / court / adversarial)

**Décision** : chaque scénario haut-niveau génère ensuite trois variantes correspondant aux familles d'évaluation. À ce stade, seul le scénario « idéal » est documenté en grandes lignes ; les variantes court et adversarial sont implicites et seront générées lors de la phase de rédaction.

**Rationale** : surcharger cette phase avec les trois variantes nuirait à la lisibilité et ralentirait la validation de la couverture fonctionnelle.

---

### Format des grandes lignes d'un scénario

**Décision** : chaque scénario décrit les éléments suivants (sans dialogues détaillés) :
- **ID** : identifiant unique (`<persona>-<scope>-<n>`)
- **Titre** : phrase courte décrivant l'intention
- **Complexité** : Simple / Complexe
- **Résumé** : 1-3 phrases expliquant le contexte, l'intention et l'enjeu
- **Tools MCP impliqués** : liste des outils attendus (moteur de tarification, vue portefeuille, etc.)

**Rationale** : ce format est suffisant pour valider la couverture et lancer la génération détaillée.

## Risks / Trade-offs

- **[Risque] Couverture inégale selon les personas** : certains personas (ex. Nathalie — santé collective) ont un univers très spécifique et des scénarios transversaux sont moins naturels. → Mitigation : accepter qu'un persona puisse avoir moins de scénarios complexes si son périmètre ne s'y prête pas.
- **[Risque] Chevauchement entre les deux périmètres** : un scénario complexe peut légitimement couvrir tarification ET suivi (ex. relance d'un devis expiré). → Mitigation : classer selon le périmètre d'entrée de l'interaction ; croiser si nécessaire.
- **[Trade-off] Granularité vs lisibilité** : plus de scénarios améliore la couverture mais alourdit la validation. → Choix : 2-3 scénarios simples + 1-2 complexes par persona par périmètre.
