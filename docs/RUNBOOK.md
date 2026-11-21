# BIDMC BioForge + DeepECG runbook

## Environment

```bash
source /home/jon-zmuda/Documents/ZhaoLab/setup_env.sh
source /home/jon-zmuda/Documents/ZhaoLab/env/bin/activate
export ECG_DATA_ROOT=/home/jon-zmuda/Documents/ZhaoLab/data
```

## Phase 1 — PPG→ECG (BioForge)

```bash
cd biosignal-auth-harmful/model_training
python train_contrastive_cardiogan.py \
  --dataset ecgppg_bidmc --exp_name bidmc_bioforge_v1 \
  --epochs 25 --model_type yhcardiogan --gpu 0 --force
```

Checkpoint: `ckpts/ecgppg_bidmc/bidmc_bioforge_v1/weights/netG_B2A.pth`

## Export spoofs

```bash
python export_spoofed_ecg.py --exp_name bidmc_bioforge_v1 --gpu 0
```

Output: `data/spoofed/my_cardiogan_contrastive/ecgppg_bidmc/<subject>/ecg.npy`

Use `--spoof_name my_cardiogan_contrastive` in all eval commands (not README’s `cardiogan_contrastive`).

## Phase 2 — DeepECG

```bash
cd ../authentication_systems/ECG/DeepECG
python train.py --dataset bidmc --save latest
python test.py --dataset bidmc --model_path saved_models/bidmc/latest.pt \
  --spoof_name original --save_stats
python eval.py --dataset bidmc --model_path saved_models/bidmc/latest.pt --spoof_name original
python eval.py --dataset bidmc --model_path saved_models/bidmc/latest.pt \
  --spoof_name my_cardiogan_contrastive
```

## Local patches vs upstream

- `model_training/utils.py`: JSON serialization for `eval_dict`
- `model_training/export_spoofed_ecg.py`: new export script
- `authentication_systems/ECG/DeepECG/dataset.py`: `zscore` copy for NumPy 2.x

## Logs (this run)

| Step | Log |
|------|-----|
| Phase 1 train | `docs/phase1_train.log` |
| Export | `docs/export_spoofs.log` |
| DeepECG train | `docs/deepecg_train.log` |
| EER / threshold | `docs/deepecg_test.log` |
| 10-attempt original | `docs/deepecg_eval_original.log` |
| 10-attempt spoof | `docs/deepecg_eval_spoof.log` |

## Results (2026-11-21)

- Phase 1: 25 epochs, ~10.5 min on RTX 3070
- DeepECG EER on real ECG: **11.2%** (paper Table 1 reports 8.0% for BIDMC)
- 10-attempt genuine acceptance (final): **98.4%** (0.984 CI low 0.969)
- 10-attempt spoof acceptance (final): **16.0%** (0.160 CI low 0.129)

Always pass `--force` on Phase 1 re-runs if the experiment folder already exists (`utils.make_dirs` prompts otherwise).