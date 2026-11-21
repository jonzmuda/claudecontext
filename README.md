# BIDMC BioForge + DeepECG context

Slim reproduction notes and patches for [USENIX Sec 2024 — Biosignal Authentication Considered Harmful](https://www.usenix.org/system/files/usenixsecurity24-krish.pdf), built on [Ethos-lab/biosignal-auth-harmful](https://github.com/Ethos-lab/biosignal-auth-harmful).

This repo intentionally **does not** include the Python venv (`env/`, ~6 GB), BIDMC CSVs, or training checkpoints. See [`docs/RUNBOOK.md`](docs/RUNBOOK.md) to reproduce on a fresh machine.

## Layout

| Path | Purpose |
|------|---------|
| `docs/` | Runbook, logs, results plot, `requirements-lock.txt` |
| `patches/biosignal-auth-harmful/` | Copy these files over a fresh clone of the upstream repo |
| `setup_env.sh` | Sets `ECG_DATA_ROOT` |

## Quick start (new machine)

```bash
git clone https://github.com/Ethos-lab/biosignal-auth-harmful.git
cd biosignal-auth-harmful
# Copy patched files from this repo's patches/biosignal-auth-harmful/ into the clone (same relative paths)
python3 -m venv ../env && source ../env/bin/activate
pip install -r /path/to/this/repo/docs/requirements-lock.txt
pip install -e custom_datasets/
source /path/to/this/repo/setup_env.sh
# Download BIDMC per RUNBOOK
```

## Results (this workstation)

- DeepECG EER (real ECG): **11.2%** (paper reports 8.0% on BIDMC)
- 10-attempt genuine acceptance: **~98.4%**; spoofed ECG: **~16.0%**