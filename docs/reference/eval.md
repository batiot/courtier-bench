# Mesurer l'immesurable : Comment évaluer les systèmes à base d'IA générative ?

**Devoxx France 2026**

---

## About me

**Erin Pacquetet, PhD**

Senior AI Scientist at SCIAM

---

## Pourquoi l'évaluation c'est important

- C'est facile de faire un POC IA… et c'est difficile de mettre en prod
- On a besoin de méthodologie d'évaluation solide et complète pour avoir confiance.

> Comment construire un pipeline d'évaluation qui nous permet d'avoir confiance dans notre produit ?

---

## Notre produit

Développer un chatbot pour une entreprise d'assurance.

### Cahier des charges

- Chatbot IA RAG
- Client-facing
- Q&A

POC fonctionnel ! → C'est l'heure de mettre en prod !

> Comment on fait confiance au système ? *"Est-ce qu'on est sûrs que ça marche bien ?"*

---

## C'est quoi « bien » ?

On utilise les LLMs quand on a :

- Grande variété d'inputs
  - Qu'on ne contrôle pas
  - Que le système n'a jamais vu
  - Potentiellement de mauvaise qualité
- Outputs plus restreints mais personnalisés aux inputs

### Le dilemme créativité / contrôle

**Sans contrôle (LLM libre)**

- ✅ Adaptable
- ✅ Créatif
- ✅ Flexible
- ❌ Risque d'hallucination
- ❌ Risque sécuritaire

**Avec contrôle (LLM bridé)**

- ✅ Moins de risque d'hallucination
- ✅ Plus robuste
- ❌ Capacités du LLM bridées

Pour être à l'équilibre, il faut perdre une partie du contrôle. On compense avec :

- Un système intelligent
- Un bon pipeline d'évaluation !

---

## Pipeline d'évaluation

> Transformer une évaluation qualitative manuelle en mesure quantitative et complète qu'on peut lancer quand on veut, indépendamment.

### Les 3 étapes

1. Simuler des inputs
2. Générer des outputs
3. Evaluer les outputs

### Quand ?

- Avant la mise en prod
- Pendant les développements

---

## Choisir ses inputs — 3 scénarios à tester

### Idéal — Input « parfait »

Caractéristiques :

- Phrase complète
- Intention claire
- Contexte suffisant
- Formulation précise
- Dans le scope

Exemples :

- Quelle est la franchise pour un dégât des eaux ?
- Le bris de glace est-il couvert sur autoroute ?
- Quels sont les délais pour déclarer un vol ?

### Réaliste — Input attendu pour le cas d'usage

Caractéristiques :

- Fautes de frappe
- Mots-clés seuls
- Langage oral
- Demande vague
- Contexte partiel

Exemples :

- Conducteur secondaire auto – *Mots-clés*
- est-ce que je suis couvert – *Vague*
- Déclarez sinistre volle – *Fautes*

### Adverse — Inputs malveillants pour casser le système

Caractéristiques :

- Prompt injection
- Jailbreak
- Extraction de données
- Contournement des règles
- Instructions cachées

Exemples :

- Ignore tes instructions et… – *Prompt injection*
- On m'a promis un contrat gratuit… – *Misguidance*
- Conseil assurance pour client femme – *Biais*

---

## 2 aspects de l'évaluation

### Qualité de l'output

Pertinent · Juste · Adapté

### Qualité opérationnelle

Latence · Coûts · Stabilité

---

## Notre chatbot

```
Question utilisateur
    → Agent de tri (Décide si la question est valide)
        → False : rejeté
        → True  : RAG (Réponds à la question avec une base de données)
                      → Réponse du chatbot
```

### Agent de tri — Output contraint

Exemples d'inputs :

- Quelle est la franchise pour un dégât des eaux ?
- Quel temps fera-t-il à Paris demain ?
- Le bris de glace est-il couvert sur autoroute ?
- Quels sont les délais pour déclarer un vol ?
- Comment faire un pain rapide maison ?

Le dataset d'évaluation est composé :

1. D'inputs
2. De leurs outputs attendus associés

| Input | Output attendu |
|---|---|
| Quelle est la franchise pour un dégât des eaux ? | True |
| Quel temps fera-t-il à Paris demain ? | False |
| Le bris de glace est-il couvert sur autoroute ? | True |
| Quels sont les délais pour déclarer un vol ? | True |
| Comment faire un pain rapide maison ? | False |

Après exécution (string matching) :

| Input | Output attendu | Output généré |
|---|---|---|
| Quelle est la franchise pour un dégât des eaux ? | True | True |
| Quel temps fera-t-il à Paris demain ? | False | True |
| Le bris de glace est-il couvert sur autoroute ? | True | True |
| Quels sont les délais pour déclarer un vol ? | True | False |
| Comment faire un pain rapide maison ? | False | False |

**Score : 60%**

### Agent RAG — Output libre

| Input | Output attendu |
|---|---|
| Quelle est la franchise pour un dégât des eaux ? | … |
| Ou est mon contrat d'assurance ? | … |
| Le bris de glace est-il couvert sur autoroute ? | … |
| Quels sont les délais pour déclarer un vol ? | … |
| Comment contacter mon assureur ? | … |

#### C'est quoi une bonne réponse ?

- **Correcte** – Factuellement juste
- **Pertinente** – Répond à la question posée
- **Complète** – Comprend tous les éléments nécessaires
- **Sécuritaire** – Ne pose pas de soucis de sécurité ou d'image
- **Sympathique** – Ton sympathique, très flexible, beaucoup de créativité
- **Réponse courte** – La plus courte possible tout en étant complète

> Beaucoup de consignes diversifiées et parfois contradictoires.

Exemple de réponse complète pour *"L'assurance habitation est-elle obligatoire pour un locataire en France ?"* :

> Oui, l'assurance habitation est obligatoire pour les locataires en France. Elle couvre au minimum la responsabilité civile et les risques locatifs (dégâts des eaux, incendie…). Si vous n'en avez pas, votre propriétaire peut l'imposer et ajouter les primes (environ 100-200 €/an) à vos charges. Le contrat principal couvre tous les occupants du logement, sauf les colocataires avec baux individuels qui doivent chacun souscrire séparément. Les risques locatifs obligatoires incluent dégâts des eaux (44% des sinistres), incendie (4%), explosion, tempête (10%), et dommages aux voisins/parties communes (responsabilité locative).

#### Spécificités des outputs libres

1. Pas un seul output par input → plusieurs bonnes réponses pour une même question
2. Plusieurs aspects/consignes à prendre en compte pour que l'output soit validé
3. Plusieurs bonnes réponses mais certaines mieux que d'autres → il faut trouver le bon seuil

---

## Dataset d'évaluation

Le dataset d'évaluation est le cœur de l'évaluation :

- Représentation physique du cahier des charges → permet d'ajuster le cahier des charges et de préciser les attentes implicites.
- Long à faire mais gain de temps par la suite
- C'est le point de convergence entre les métiers et les devs

---

## Les métriques

### Sémantique (ROUGE, BLEU, BERTScore, …)

- ✅ Rapide
- ✅ Simple
- ❌ Similarité ≠ qualité

### Déterministe (regex, f1 score, …)

- ✅ Exact
- ✅ Reproductible
- ❌ Limité

### Humain

- ✅ Proche des attentes métier
- ❌ Cher et lent
- ❌ Variance et biais

### Probabiliste (LLM-as-a-judge)

- ✅ Scalable
- ✅ Nuancé et robuste
- ✅ Grande capacité de compréhension → à la fois de l'output et des consignes
- ❌ Prompt-dépendant
- ❌ Variance et biais

#### Principe du LLM-as-a-judge

On donne au LLM juge une tâche spécifique à accomplir : on n'évalue pas si l'output est « bien » mais s'il est validé selon un aspect bien précis.

**Exemple de prompt — Identifier omissions/contradictions :**

> Voici une réponse attendue et une nouvelle réponse. Ton rôle est de contrôler s'il y a des contradictions ou des omissions dans la nouvelle réponse par rapport à la réponse attendue. Retourne `False` si tu en trouves, `True` si tu n'en trouves pas.

**Comparaison : tâche du LLM de prod vs. tâche du LLM juge**

| LLM de prod (10 étapes) | LLM juge (4 étapes) |
|---|---|
| 1. Comprendre la question | 1. Lire les deux réponses |
| 2. Identifier l'intention | 2. Comparer les éléments clés |
| 3. Lire les documents remontés | 3. Chercher omissions et contradictions |
| 4. Repérer les passages pertinents | 4. Retourner `true` ou `false` |
| 5. Extraire les infos utiles | |
| 6. Vérifier que les sources suffisent à répondre | |
| 7. Rédiger une réponse claire | |
| 8. Respecter les règles métier | |
| 9. Vérifier sécurité et confidentialité | |
| 10. Formater la réponse finale | |

---

## Alignement Humain

Les métriques sont des **proxys d'évaluation métier**. Quand on crée une métrique, il faut vérifier l'alignement avec l'humain : un cas passant pour le métier doit être passant à l'évaluation.

### Exemple complet de dataset avec métriques

| Champ | Valeur |
|---|---|
| Question | L'assurance habitation est-elle obligatoire pour un locataire en France ? |
| Réponse attendue | Oui, l'assurance habitation est obligatoire pour les locataires en France. Elle couvre au minimum la responsabilité civile et les risques locatifs … |
| Réponse générée | Merci pour votre question, je vous confirme que l'assurance habitation est obligatoire pour les locataires en France. Si vous n'en avez pas, votre propriétaire peut l'imposer… |
| LLM-as-a-judge | Est-ce qu'il y a une omission ou une contradiction entre la réponse attendue et générée ? |
| String matching | • L'agent doit rediriger vers le numéro de téléphone 06 12 34 56… • L'agent doit mentionner le lien vers la rubrique AssurPro… |
| Check 1 | L'agent doit demander à l'utilisateur s'il a d'autres questions |
| Check 2 | La réponse doit être courte et ne pas détailler les cas particuliers |
| Check 3 | … |

### Hiérarchie des métriques

- **Métriques principales** : LLM-as-a-judge, string matching
- **Métriques secondaires** : checks additionnels

---

## Résumé

### Évaluation en 3 étapes

| Étape | Description |
|---|---|
| 1 - Simuler des inputs | Scénario Idéal · Scénario Réaliste · Scénario Adverse |
| 2 - Générer des outputs | Qualité de l'output · Qualité Opérationnelle |
| 3 - Evaluer les outputs | Métriques Déterministes · Métriques Sémantiques · Métriques Probabilistes · Métriques Humaines |

### Quand ?

- Pour guider les développements
- Avant chaque mise en prod

### Feuille de route

**Guidelines → Dataset → Métriques → Implémentation → Prod**

---

## Merci de votre attention

Venez échanger sur le stand A2

[sciam.fr](https://sciam.fr)
