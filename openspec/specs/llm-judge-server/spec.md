## ADDED Requirements

### Requirement: Serveur LLM démarrable en une commande
Le serveur LLM SHALL démarrer via `docker compose up` depuis le répertoire `llm/` sans configuration manuelle préalable autre que la présence du fichier GGUF dans `llm/models/`.

#### Scenario: Démarrage nominal
- **WHEN** le fichier GGUF est présent dans `llm/models/` et l'on exécute `docker compose up` dans `llm/`
- **THEN** le serveur écoute sur `http://localhost:8080` et répond à `GET /health` avec HTTP 200

#### Scenario: GGUF absent
- **WHEN** le fichier GGUF est absent de `llm/models/`
- **THEN** `docker compose up` échoue avec un message d'erreur lisible indiquant que le modèle est manquant, et `download.sh` est mentionné comme remède

### Requirement: API OpenAI-compatible exposée
Le serveur SHALL exposer un endpoint `POST /v1/chat/completions` compatible avec le format OpenAI Chat Completions.

#### Scenario: Appel de jugement nominal
- **WHEN** une requête POST est envoyée à `/v1/chat/completions` avec un message system et un message user valides
- **THEN** le serveur retourne une réponse JSON avec un champ `choices[0].message.content` non vide dans un délai inférieur à 30 secondes

#### Scenario: Thinking mode désactivé
- **WHEN** le serveur reçoit une requête sans token `<|think|>` dans le system prompt
- **THEN** la réponse ne contient pas de bloc de raisonnement intermédiaire — uniquement la réponse finale

### Requirement: Téléchargement du modèle via script
Le dépôt SHALL fournir un script `llm/download.sh` qui télécharge le fichier GGUF depuis Hugging Face et vérifie son intégrité par SHA256.

#### Scenario: Téléchargement réussi
- **WHEN** `llm/download.sh` est exécuté sur une machine avec accès internet
- **THEN** le fichier GGUF est présent dans `llm/models/` et son SHA256 correspond à la valeur référencée dans `llm/config.yml`

#### Scenario: Fichier déjà présent
- **WHEN** `llm/download.sh` est exécuté et le fichier GGUF est déjà présent avec le bon SHA256
- **THEN** le script affiche un message de confirmation et ne re-télécharge pas le fichier

### Requirement: Modèle et configuration versionnés
Le fichier `llm/config.yml` SHALL référencer le modèle par son nom, son SHA256 et son URL source, permettant la reproductibilité entre machines.

#### Scenario: Configuration complète
- **WHEN** `llm/config.yml` est présent dans le dépôt
- **THEN** il contient au minimum : le nom du modèle, le SHA256, l'URL de téléchargement, le port d'écoute et le nombre de threads CPU
