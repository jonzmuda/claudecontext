# Apply patches

From the root of a fresh `biosignal-auth-harmful` clone:

```bash
REPO_ROOT="$(pwd)"
PATCHES="/path/to/claudecontext/patches/biosignal-auth-harmful"

cp "$PATCHES/model_training/export_spoofed_ecg.py" "$REPO_ROOT/model_training/"
cp "$PATCHES/model_training/utils.py" "$REPO_ROOT/model_training/"
cp "$PATCHES/model_training/train_contrastive_cardiogan.py" "$REPO_ROOT/model_training/"
cp "$PATCHES/authentication_systems/ECG/DeepECG/dataset.py" \
   "$REPO_ROOT/authentication_systems/ECG/DeepECG/"
```

Or copy the whole tree:

```bash
cp -r patches/biosignal-auth-harmful/model_training/* biosignal-auth-harmful/model_training/
cp patches/biosignal-auth-harmful/authentication_systems/ECG/DeepECG/dataset.py \
   biosignal-auth-harmful/authentication_systems/ECG/DeepECG/
```