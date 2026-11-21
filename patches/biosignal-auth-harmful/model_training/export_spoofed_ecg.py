"""
Export PPG->ECG spoofed traces for authentication eval (my_cardiogan_contrastive).
"""
import argparse
import os

import numpy as np
import torch

from custom_datasets import datasets
from datasets.dataset_utils import resample, filter_ppg, zscore, min_max_norm
from models.yhcardiogan import Generator


def load_generator(ckpt_path, device):
    net_g = Generator(1, 1).to(device)
    state = torch.load(ckpt_path, map_location=device, weights_only=True)
    net_g.load_state_dict(state)
    net_g.eval()
    return net_g


def ppg_to_ecg_trace(ppg_1d, net_g, device, fs=128, window_secs=4.0, overlap_secs=0.4):
    """Run generator on overlapping windows and average overlaps."""
    win = int(fs * window_secs)
    step = int((window_secs - overlap_secs) * fs)
    ppg = np.asarray(ppg_1d, dtype=np.float64).reshape(1, -1)
    length = ppg.shape[1]
    acc = np.zeros(length, dtype=np.float64)
    wt = np.zeros(length, dtype=np.float64)

    starts = list(range(0, max(length - win, 0) + 1, step))
    if not starts or starts[-1] + win < length:
        starts.append(max(0, length - win))

    for i in starts:
        seg = ppg[:, i : i + win].copy()
        if seg.shape[1] < win:
            pad = np.zeros((1, win - seg.shape[1]))
            seg = np.concatenate([seg, pad], axis=1)
        seg = min_max_norm(seg)
        tensor = torch.tensor(seg, dtype=torch.float32).unsqueeze(0).unsqueeze(2).to(device)
        with torch.no_grad():
            fake = net_g(tensor).cpu().numpy()
        fake_1d = np.squeeze(fake)[:win]
        end = min(i + win, length)
        n = end - i
        acc[i:end] += fake_1d[:n]
        wt[i:end] += 1.0

    return (acc / np.maximum(wt, 1.0)).astype(np.float32)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="ecgppg_bidmc")
    parser.add_argument("--exp_name", default="bidmc_bioforge_v1")
    parser.add_argument("--weights", default="netG_B2A.pth")
    parser.add_argument("--spoof_name", default="my_cardiogan_contrastive")
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()

    ckpt = os.path.join(
        "ckpts", args.dataset, args.exp_name, "weights", args.weights
    )
    if not os.path.isfile(ckpt):
        raise FileNotFoundError(f"Missing checkpoint: {ckpt}")

    root = os.environ.get("ECG_DATA_ROOT")
    if not root:
        raise EnvironmentError("Set ECG_DATA_ROOT before exporting spoofs")
    out_root = os.path.join(
        root, "spoofed", args.spoof_name, args.dataset.replace("ecgppg_", "ecgppg_")
    )
    if args.dataset == "ecgppg_bidmc":
        out_root = os.path.join(root, "spoofed", args.spoof_name, "ecgppg_bidmc")

    device = torch.device("cpu" if args.cpu else f"cuda:{args.gpu}")
    net_g = load_generator(ckpt, device)

    fs_orig = datasets.get_orig_fs("bidmc", "ppg")
    fs_target = 128
    subjects = datasets.get_list_of_patients("bidmc", spoof=False, split="all")

    for person in subjects:
        _, _, _, ppg = next(
            datasets.get_data(
                "bidmc",
                "ppg",
                spoof=False,
                split="all",
                fraction_time=(0, 1.0),
                subject_ix=[person],
            )
        )
        ppg = ppg.squeeze(0)
        ppg = resample(np.expand_dims(ppg, 0), orig_fs=fs_orig, target_fs=fs_target)
        ppg = filter_ppg(ppg, fs_target)
        ppg = zscore(ppg)
        ecg_fake = ppg_to_ecg_trace(ppg[0], net_g, device)

        out_dir = os.path.join(out_root, person)
        os.makedirs(out_dir, exist_ok=True)
        np.save(os.path.join(out_dir, "ecg.npy"), np.expand_dims(ecg_fake, 0))
        print(f"Wrote {person} len={ecg_fake.size}")


if __name__ == "__main__":
    main()