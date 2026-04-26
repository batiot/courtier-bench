#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/models"
CONFIG="$SCRIPT_DIR/config.yml"

# Read config values (requires yq or python)
if command -v python3 &>/dev/null; then
    MODEL_URL=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['model']['url'])")
    MODEL_FILE=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['model']['filename'])")
    MODEL_REPO=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['model'].get('repo', ''))")
    EXPECTED_SHA256=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['model']['sha256'])")
else
    echo "ERROR: python3 is required to read config.yml"
    exit 1
fi

DEST="$MODELS_DIR/$MODEL_FILE"

mkdir -p "$MODELS_DIR"

# Skip download if file already exists with correct SHA256
if [[ -f "$DEST" ]] && [[ -n "$EXPECTED_SHA256" ]]; then
    ACTUAL_SHA256=$(sha256sum "$DEST" | awk '{print $1}')
    if [[ "$ACTUAL_SHA256" == "$EXPECTED_SHA256" ]]; then
        echo "✓ Model already present and verified: $MODEL_FILE"
        exit 0
    else
        echo "⚠ SHA256 mismatch — re-downloading..."
    fi
fi

echo "Downloading $MODEL_FILE..."
echo "Source: $MODEL_URL"

# HuggingFace token — required for gated models (Gemma license)
# Set via: export HF_TOKEN=hf_xxxxx  (or pass as argument)
HF_TOKEN="${HF_TOKEN:-${1:-}}"
if [[ -z "$HF_TOKEN" ]]; then
    echo "ERROR: HuggingFace token required (gated model)."
    echo "  1. Accept the Gemma license at https://huggingface.co/google/gemma-4-E2B-it"
    echo "  2. Create a Read token at https://huggingface.co/settings/tokens"
    echo "  3. Run:  export HF_TOKEN=hf_xxxxx && bash download.sh"
    exit 1
fi

# Use huggingface-cli if available, otherwise wget with Bearer auth
if command -v huggingface-cli &>/dev/null; then
    HF_TOKEN="$HF_TOKEN" huggingface-cli download "$MODEL_REPO" \
        "$MODEL_FILE" \
        --local-dir "$MODELS_DIR"
elif command -v wget &>/dev/null; then
    wget --header="Authorization: Bearer $HF_TOKEN" -O "$DEST" "$MODEL_URL"
elif command -v curl &>/dev/null; then
    curl -L -H "Authorization: Bearer $HF_TOKEN" -o "$DEST" "$MODEL_URL"
else
    echo "ERROR: wget or curl is required"
    exit 1
fi

# Verify SHA256 if configured
if [[ -n "$EXPECTED_SHA256" ]]; then
    ACTUAL_SHA256=$(sha256sum "$DEST" | awk '{print $1}')
    if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
        echo "ERROR: SHA256 mismatch after download!"
        echo "  Expected: $EXPECTED_SHA256"
        echo "  Got:      $ACTUAL_SHA256"
        rm -f "$DEST"
        exit 1
    fi
    echo "✓ SHA256 verified"
else
    ACTUAL_SHA256=$(sha256sum "$DEST" | awk '{print $1}')
    echo "SHA256 (update config.yml): $ACTUAL_SHA256"
fi

echo "✓ Model ready: $DEST"
