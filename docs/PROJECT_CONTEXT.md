# Project context (for humans and Claude)

## What you asked for

Reproduce part of **“Biosignal Authentication Considered Harmful Today”** (Krish et al., USENIX Security 2024) on **Linux** after Windows blocked Phase 2.

Sources you provided:

- [Paper PDF](https://www.usenix.org/system/files/usenixsecurity24-krish.pdf)
- [Ethos-lab/biosignal-auth-harmful](https://github.com/Ethos-lab/biosignal-auth-harmful)
- Slide deck: *Jons Slide November 18.pdf* (BIDMC-only scope, temporal splits, BioForge smoke test)

### Scope you chose (plan interview)

| Decision | Your choice |
|----------|-------------|
| Dataset | **BIDMC only** (not CAPNO/DALIA/WESAD combined training) |
| Generator | PPG→ECG BioForge / `yhcardiogan`, `--dataset ecgppg_bidmc` |
| Authentication | **One system: DeepECG** (not ECGXtractor / EDITH / KeyToYourHeart) |
| Phase 1 | **Train from scratch** on this Linux machine (no Windows checkpoints) |
| Data download | PhysioNet BIDMC (open zip, no account) |
| Success criteria | **Full pipeline works**: train → export spoofs → train auth → 10-attempt eval with logs/plots |
| Out of scope (for now) | Cross-modality attacks, video→ECG, all auth systems, exact match to paper Figure 6 numbers |

### Intended protocol (from slides + repo)

Per-subject trace split along **time** (same subject IDs everywhere):

- **0–50%** — BioForge train/test windows  
- **50–67.5%** — DeepECG training clips  
- **67.5–75%** — threshold / monitoring on real ECG  
- **75–100%** — spoof attack evaluation  

Spoof data path convention: `my_cardiogan_contrastive` (not README typo `cardiogan_contrastive`).

---

## What was done

### Environment and layout

- Cloned upstream repo under `ZhaoLab/biosignal-auth-harmful/`
- Set `ECG_DATA_ROOT=/home/jon-zmuda/Documents/ZhaoLab/data` via `setup_env.sh`
- Python **3.13** venv at `ZhaoLab/env/` (PyTorch **CUDA**, RTX 3070)
- Installed missing runtime deps discovered during runs: `biosppy`, `peakutils`, `wandb`, `librosa`

### Data

- Downloaded BIDMC (~208 MB zip) → `data/bidmc/` (106 CSV files)
- Validated loader: subject `05`, ECG shape `(1, 6000)` for a short `fraction_time` slice

### Phase 1 — PPG→ECG training

- Command: `train_contrastive_cardiogan.py --dataset ecgppg_bidmc --exp_name bidmc_bioforge_v1 --epochs 25 --model_type yhcardiogan --gpu 0 --force`
- Runtime ~**10.5 minutes** on RTX 3070
- Checkpoint: `model_training/ckpts/ecgppg_bidmc/bidmc_bioforge_v1/weights/netG_B2A.pth` (PPG→ECG)
- Training plots under `ckpts/.../images_best/`

### Code changes vs upstream (in `patches/biosignal-auth-harmful/`)

| File | Why |
|------|-----|
| `model_training/utils.py` | Fix `float32` not JSON serializable when writing `eval_dict.json` |
| `model_training/train_contrastive_cardiogan.py` | Use `default=utils._json_serializable` in `json.dump` |
| `model_training/export_spoofed_ecg.py` | **New** — upstream had no spoof export; writes `data/spoofed/my_cardiogan_contrastive/ecgppg_bidmc/<id>/ecg.npy` |
| `authentication_systems/ECG/DeepECG/dataset.py` | `zscore()` copies array (NumPy 2.x read-only buffer) |

### Phase 1.5 — Export spoofs

- Exported **45 subjects** (train+test IDs in `properties.py`) at 128 Hz
- Log: `docs/export_spoofs.log`

### Phase 2 — DeepECG

1. `train.py --dataset bidmc --save latest` (100 epochs; ~82% train acc)
2. `test.py ... --save_stats` → EER threshold saved in `latest.pt`
3. `eval.py` ×2: `original` vs `my_cardiogan_contrastive` (10 attempts each)

### Results (this machine, 2026-11-21)

| Metric | Value | Paper reference (BIDMC / DeepECG) |
|--------|-------|-----------------------------------|
| EER on real ECG | **11.2%** | Table 1: **8.0%** |
| Genuine acceptance @ attempt 10 | **~98.4%** | Fig. 6 solid line (qualitative) |
| Spoof acceptance @ attempt 10 | **~16.0%** | Fig. 6 dashed (paper often >>50% on many systems) |

Interpretation: **Pipeline milestone met**; spoof attack on this BIDMC-only generator run is **weaker** than the paper’s headline curves (expected gaps: single-dataset training, repo `γ=30` vs paper `γ=100`, one seed).

Artifacts: `docs/*.log`, `docs/acceptance_curve_bidmc_deepecg.png`, `docs/RUNBOOK.md`, `docs/requirements-lock.txt`.

---

## What this Git repo contains (claudecontext)

**Uploaded (~260 KB):** context, runbook, logs, plots, patches, `.gitignore`, `setup_env.sh`.

**Not uploaded (reproduce locally):**

- `env/` (~6.1 GB venv)
- `data/bidmc/` (~147 MB; public download)
- `data/spoofed/` (regenerate with `export_spoofed_ecg.py`)
- GAN weights (~216 MB) and `saved_models/bidmc/latest.pt` (~4 MB) — optional; use Git LFS if you add them later

---

## Problems hit along the way

1. **Windows → Linux** — upstream assumed Linux paths and tooling (motivation for move).  
2. **Phase 1 smoke test** — `float32` JSON crash (patched).  
3. **Missing packages** — `wandb`, `librosa`, `biosppy`/`peakutils` not in upstream requirements.  
4. **DeepECG** — read-only NumPy array in `zscore` (patched).  
5. **Export script** — tensor shape for 4D CardioGAN; `get_paired_data` quirk (switched to `get_data` per subject).

---

## References

- Paper: Krish et al., USENIX Security 2024 — [PDF](https://www.usenix.org/system/files/usenixsecurity24-krish.pdf)  
- Code: https://github.com/Ethos-lab/biosignal-auth-harmful  
- BIDMC: https://physionet.org/content/bidmc/1.0.0/  