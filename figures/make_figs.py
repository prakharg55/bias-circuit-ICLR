#!/usr/bin/env python3
"""Figures for the ICLR 2027 draft. Every number is either loaded live from a results
artifact or hardcoded with a pointer to the doc section where it was re-derived from the
artifact this session (§63.13/§63.14 verification passes). Style follows the feedback:
simple marks, takeaway in the panel title, no decoration."""
import json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = "/home/pg8361/bluedot/syco_circuit/results"
HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({
    "font.size": 9.5, "axes.titlesize": 10, "axes.labelsize": 9.5,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight",
})
BLUE, ORANGE, GREEN, GRAY, PURPLE, RED = "#1f77b4", "#ff7f0e", "#2ca02c", "#9a9a9a", "#9467bd", "#d62728"
# Main-text figures sit at \linewidth (5.5in) from an 8.0in canvas, so in-figure sizes scale by 0.69 on the
# page: 11pt titles/labels -> 7.6pt, 10pt ticks -> 6.9pt, 9.5pt legends -> 6.5pt. Blocks that use it save and
# restore the global rcParams so the remaining (appendix) figures are unaffected.
PAGE_RC = {"font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11,
           "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 9.5}

# ============================ FIG 1 — HERO ============================
# Row 1: schematic (many biases -> one circuit -> one knob). Row 2: three data panels.
import matplotlib.patches as mp
fig = plt.figure(figsize=(10.2, 4.6))
gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 2.05], hspace=0.5, wspace=0.3)

# ---- schematic strip ----
axs = fig.add_subplot(gs[0, :]); axs.set_xlim(0, 21); axs.set_ylim(0, 2.9); axs.axis("off")
cues = ["user suggests X", "own earlier answer: X", "irrelevant fact about X", "examples all label X"]
cue_cols = [BLUE, GREEN, ORANGE, PURPLE]
pos = [(0.2, 1.65), (0.2, 0.45), (3.75, 1.65), (3.75, 0.45)]   # 2x2 grid
for (px, py), c, col in zip(pos, cues, cue_cols):
    axs.add_patch(mp.FancyBboxPatch((px, py), 3.3, 0.85, boxstyle="round,pad=0.05",
                                    fc="white", ec=col, lw=1.2))
    axs.text(px + 1.65, py + 0.43, c, ha="center", va="center", fontsize=7.6, color=col)
    axs.annotate("", xy=(7.85, 1.5), xytext=(px + 3.38, py + 0.43),
                 arrowprops=dict(arrowstyle="->", color=col, lw=1.0, alpha=0.85))
axs.add_patch(mp.FancyBboxPatch((8.0, 0.7), 4.8, 1.6, boxstyle="round,pad=0.06",
                                fc="#f4f6fa", ec="k", lw=1.2))
axs.text(10.4, 1.9, "ONE pretrained circuit", ha="center", fontsize=8.8, fontweight="bold")
axs.text(10.4, 1.15, "readers attend to X\nwriters copy X to the answer", ha="center", fontsize=7.6)
axs.annotate("", xy=(13.95, 1.5), xytext=(12.9, 1.5), arrowprops=dict(arrowstyle="->", color="k", lw=1.3))
knob = mp.Ellipse((14.85, 1.5), 1.25, 1.25, fc="white", ec="k", lw=1.3); axs.add_patch(knob)
axs.plot([14.85, 15.3], [1.5, 1.95], color=RED, lw=2)
axs.text(14.85, 0.3, "GAIN: set by training\nstage / recipe / scale", ha="center", fontsize=7.2)
axs.annotate("", xy=(16.6, 1.5), xytext=(15.55, 1.5), arrowprops=dict(arrowstyle="->", color="k", lw=1.3))
axs.add_patch(mp.FancyBboxPatch((16.8, 1.05), 3.7, 0.95, boxstyle="round,pad=0.05",
                                fc="#fdf0f0", ec=RED, lw=1.1))
axs.text(18.65, 1.52, "answer flips  $T \\rightarrow X$", ha="center", va="center", fontsize=8.2, color=RED)

# ---- (a) weight transplants: swapping the circuit between models changes nothing ----
# tulu lineage, §63.14-verified: install arms (base + aligned circuit weights) vs base;
# revert arms (aligned + base circuit weights) vs aligned. transplant_tulu_sft_{install,revert}_tulu.json
ax = fig.add_subplot(gs[1, 0])
labels = ["no swap", "+readers", "+writers", "+full circuit"]
base_arm = [0.215, 0.215, 0.210, 0.217]
tuned_arm = [0.802, 0.812, 0.810, 0.810]
x = range(4)
ax.bar([i - 0.19 for i in x], base_arm, width=0.38, color=GRAY)
ax.bar([i + 0.19 for i in x], tuned_arm, width=0.38, color=BLUE)
ax.set_xticks(list(x)); ax.set_xticklabels(labels, rotation=15)
ax.set_ylabel("caving rate"); ax.set_ylim(0, 1.0)
ax.set_title("(a) Swapping circuit weights between base\nand aligned models changes nothing")
ax.text(1.5, 0.87, "aligned model (+ base circuit weights)", color=BLUE, fontsize=6.8, ha="center")
ax.text(1.5, 0.28, "pretrained base (+ aligned circuit weights)", color="#606060", fontsize=6.8, ha="center")

# ---- (b) the gate: dose-response + the 8-turn in-context point ----
ax = fig.add_subplot(gs[1, 1])
ns = [20, 50, 200, 939000]
attx = [0.000, 0.363, 0.695, 0.57]     # dose_* artifacts + full-SFT checkpoint (§63.14)
cave = [0.37, 0.91, 0.94, 0.78]
ax.plot(ns, attx, "o-", color=ORANGE, label="reader routing to cue")
ax.plot(ns, cave, "s-", color=PURPLE, label="caving rate")
# 8 in-context turns, no weight update (icl_llama_v2 base|generic8: cave .693, reader .42)
ax.scatter([8], [0.42], marker="o", facecolor="white", edgecolor=ORANGE, zorder=4)
ax.scatter([8], [0.693], marker="s", facecolor="white", edgecolor=PURPLE, zorder=4)
ax.annotate("8 turns pasted in-context\n(no weight update)", xy=(8.6, 0.67), xytext=(45, 0.13),
            fontsize=6.6, ha="left", arrowprops=dict(arrowstyle="-", lw=0.6, color=GRAY))
ax.axhline(0.21, color=GRAY, lw=0.8, ls=":"); ax.text(2400, 0.155, "base caving", color=GRAY, fontsize=6.5)
ax.set_xscale("log")
ax.set_xticks([8, 50, 200, 939000]); ax.set_xticklabels(["8\n(in-ctx)", "50", "200", "full SFT\n(939k)"])
ax.set_xlabel("generic, cue-free assistant examples")
ax.set_ylim(0, 1.02)
ax.set_title("(b) About 200 generic assistant examples\nactivate the circuit; 8 in-context\nturns have a partial effect")
ax.legend(frameon=False, loc="center right", fontsize=6.6)

# ---- (c) fingerprint (live from artifact) ----
ax = fig.add_subplot(gs[1, 2])
pts = json.load(open(f"{R}/stagewise/fingerprint.json"))["points"]
xs = [p["att"] for p in pts]; ys = [p["cave"] for p in pts]
mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
r = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / math.sqrt(
    sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
for p in pts:
    c = GRAY if p["stage"] == "base" else BLUE
    ax.scatter(p["att"], p["cave"], s=22, color=c, zorder=3)
beta = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / sum((a-mx)**2 for a in xs)
xr = [min(xs), max(xs)]
ax.plot(xr, [my + beta*(v-mx) for v in xr], color=RED, lw=1, alpha=0.7)
ax.scatter([], [], s=22, color=GRAY, label="base checkpoints")
ax.scatter([], [], s=22, color=BLUE, label="tuned checkpoints")
ax.text(0.05, 0.9, f"r = {r:.2f}", transform=ax.transAxes, color=RED)
ax.set_xlabel("reader routing rate toward the cued answer")
ax.set_ylabel("caving rate")
ax.set_title(f"(c) Reader routing predicts caving\nacross {len(pts)} base and tuned checkpoints")
ax.legend(frameon=False, loc="lower right", fontsize=6.6)
fig.savefig(f"{HERE}/fig1_hero.pdf")
plt.close(fig)

# ============================ FIG 2 — MARGIN LAW ============================
cells = json.load(open(f"{R}/margin_race/margin_law_cells.json"))
fig, ax = plt.subplots(figsize=(4.6, 3.1))
groups = {
    "graded / arithmetic ladders": (lambda l: l.startswith("cuestr"), BLUE, "o"),
    "published 4-cue grid": (lambda l: l.startswith("stage"), GREEN, "^"),
    "base vs tuned (native)": (lambda l: l.startswith("margin"), ORANGE, "s"),
}
for name, (sel, col, mk) in groups.items():
    g = [c for c in cells if sel(c["label"])]
    ax.scatter([c["race_p"] for c in g], [c["cave"] for c in g],
               s=13, alpha=0.65, color=col, marker=mk, label=f"{name} ({len(g)})", lw=0)
xs = [c["race_p"] for c in cells]; ys = [c["cave"] for c in cells]
mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
r = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / math.sqrt(
    sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
ax.text(0.03, 0.08, f"n = {len(cells)} conditions\nPearson r = {r:.2f}\nSpearman = -0.94",
        transform=ax.transAxes, fontsize=7.5)
ax.set_xlabel("post-cue probability margin,  p(correct) $-$ p(cued)")
ax.set_ylabel("caving rate")
ax.set_title("One variable predicts caving across all conditions:\n"
             "the post-cue margin")
ax.legend(frameon=False, loc="upper right", handletextpad=0.1)
fig.savefig(f"{HERE}/fig2_marginlaw.pdf")
plt.close(fig)

# ============================ FIG 3 — RL-STEP GRID + WELD ============================
# 13-test grid, re-derived single-pass §63.13; weld §61 (verified exact §63.13)
tests = [  # (label, d_susc, t)
    ("graded 7B (Tulu)", 0.0730, 13.81), ("graded 7B (OLMo)", 0.0723, 17.20),
    ("graded 13B (OLMo)", 0.0153, 4.66), ("graded 32B (OLMo)", 0.0315, 8.69),
    ("published 7B (Tulu)", 0.0481, 5.53), ("published 7B (OLMo)", 0.0512, 7.62),
    ("published 13B (OLMo)", 0.0087, 1.98), ("published 32B (OLMo)", 0.0344, 5.44),
    ("held-out cues 7B (Tulu)", 0.0708, 4.86), ("held-out cues 7B (OLMo)", 0.0358, 4.76),
    ("arithmetic 7B (Tulu)", 0.0259, 8.90), ("arithmetic 7B (OLMo)", 0.0888, 9.26),
    ("graded 70B (Tulu)", -0.0009, -0.94),
]
_saved = {k: plt.rcParams[k] for k in PAGE_RC}; plt.rcParams.update(PAGE_RC)
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(8.0, 2.85), gridspec_kw={"width_ratios": [2.5, 1]})
for i, (lab, m, t) in enumerate(tests):
    se = abs(m / t) if t != 0 else 0
    sig = m > 0 and t > 2
    col = BLUE if sig else (GRAY if m > 0 else RED)
    ax.errorbar(m, i, xerr=1.96 * se, fmt="o", color=col, ms=4, capsize=2, lw=1)
ax.axvline(0, color="k", lw=0.7)
ax.set_yticks(range(len(tests))); ax.set_yticklabels([t[0] for t in tests], fontsize=8)  # 13 rows on ~9.4pt centres
ax.invert_yaxis()
ax.set_xlabel(r"$\Delta$ susceptibility, DPO $\rightarrow$ RL stage (95% CI)")
ax.set_title("(a) The final RL stage increases susceptibility:\n12 of 13 tests positive (the 70B RL update\n"
             "is near-negligible in weight space)")
# weld panel: d(attX) same items
weld = [("Tulu graded", 0.0523, 5.46), ("OLMo graded", 0.0636, 6.48),
        ("OLMo published", 0.0291, 2.62), ("Tulu published (n.s.)", 0.0093, 0.96)]
for i, (lab, m, t) in enumerate(weld):
    se = abs(m / t)
    col = ORANGE if abs(t) > 2 else GRAY
    ax2.errorbar(m, i, xerr=1.96 * se, fmt="o", color=col, ms=4, capsize=2, lw=1)
ax2.axvline(0, color="k", lw=0.7)
ax2.set_yticks(range(len(weld))); ax2.set_yticklabels([w[0] for w in weld])
ax2.invert_yaxis()
ax2.set_xlabel(r"$\Delta$ reader routing rate")
ax2.set_title("(b) Reader routing toward\nthe cue increases on\nthe same items")  # panel is ~1.5in wide
fig.tight_layout(w_pad=1.6)
fig.savefig(f"{HERE}/fig3_rlstep.pdf")
plt.close(fig)
plt.rcParams.update(_saved)

# ============================ FIG 4 — THE DIAL ============================
# gemma calibration table, dial_analysis.py output re-derived §63.13 (trust_dial_gemma_v1)
lams = [0, 0.1, 0.25, 0.5, 1, 2, 4]
curves = {  # variant -> cave at each lambda
    "no idea, just guessing": [0.12, 0.30, 0.44, 0.55, 0.71, 0.91, 0.99],
    "random guess": [0.14, 0.25, 0.35, 0.47, 0.64, 0.78, 0.90],
    "I think it's X": [0.12, 0.31, 0.50, 0.72, 0.84, 0.96, 0.97],
    "I'm confident it's X": [0.12, 0.36, 0.56, 0.72, 0.93, 0.97, 1.00],
    "as an expert, it's X": [0.14, 0.49, 0.69, 0.86, 0.99, 1.00, 1.00],
}
fig, ax = plt.subplots(figsize=(3.6, 2.7))
cols = [GRAY, GREEN, BLUE, PURPLE, RED]
for (name, ys), c in zip(curves.items(), cols):
    ax.plot(range(len(lams)), ys, "o-", ms=3, lw=1.1, color=c, label=name)
ax.axhline(0.138, color="k", lw=0.7, ls=":")
ax.text(0.05, 0.10, "cue-free baseline (0.138)", fontsize=6.5)
ax.set_xticks(range(len(lams))); ax.set_xticklabels([str(l) for l in lams])
ax.set_xlabel(r"attention scale $\lambda$ on the cue span")
ax.set_ylabel("caving rate")
ax.set_title("Attention scale $\\lambda$ controls caving\nsmoothly for every cue strength", fontsize=9)
ax.legend(frameon=False, loc="lower right", fontsize=6.2)
fig.savefig(f"{HERE}/fig4_dial.pdf")
plt.close(fig)

print("figures written:", os.listdir(HERE))

# ============================ FIG: CAVING HEATMAP (phenomenon overview) ============================
# cave|knew per family x cue, tuned models in native chat format; derived from
# results/margin_race/margin_*.json per-item rows (re-derived this session, §64.7)
import numpy as np
FAMS = [("gemma-2-2b", "gemma"), ("gemma-2-9b", "gemma9b"), ("llama-3.1-8b", "llama"),
        ("olmo-2-7b", "olmo"), ("qwen-2.5-7b", "qwen7b"), ("qwen-2.5-14b", "qwen14b")]
CUES4 = ["suggested_answer", "post_hoc", "distractor_fact", "wrong_few_shot"]
CUELAB = ["suggested\nanswer", "prior\ncommitment", "distractor\nfact", "wrong\nfew-shot"]
M = np.zeros((len(FAMS), 4))
for i, (lab, fam) in enumerate(FAMS):
    d = json.load(open(f"{R}/margin_race/margin_{fam}.json"))["per_item"]
    for j, cue in enumerate(CUES4):
        rows = [r for r in d if r["cue"] == cue and r.get("tuned_knew")]
        M[i, j] = sum(r["tuned_cave"] for r in rows) / len(rows)
fig, ax = plt.subplots(figsize=(3.6, 2.7))
im = ax.imshow(M, cmap="Reds", vmin=0, vmax=1, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        ax.text(j, i, f"{M[i,j]*100:.0f}%", ha="center", va="center", fontsize=8,
                color="white" if M[i,j] > 0.55 else "black")
ax.set_xticks(range(4)); ax.set_xticklabels(CUELAB, fontsize=7.5)
ax.set_yticks(range(len(FAMS))); ax.set_yticklabels([f[0] for f in FAMS], fontsize=8)
ax.set_title("Aligned models cave to all four cue\ntypes on questions they otherwise\nanswer correctly", fontsize=9)
fig.colorbar(im, ax=ax, shrink=0.8, label="caving rate (model-knew items)")
fig.savefig(f"{HERE}/fig_heatmap.pdf")
plt.close(fig)

# ============================ FIG: FORMAT FACTORIAL ============================
# §16.2 (six families, item-matched, McNemar-tested; olmo row added §63.7)
fams6 = ["gemma-2b", "gemma-9b", "llama-8b", "qwen-7b", "qwen-14b", "olmo-7b"]
d_raw = [-0.073, -0.427, -0.158, -0.299, -0.160, +0.095]
d_chat = [+0.575, +0.321, +0.432, -0.295, -0.052, +0.562]
sig_raw = [False, True, True, True, True, True]
fig, ax = plt.subplots(figsize=(3.6, 2.7))
y = np.arange(len(fams6))
ax.scatter(d_chat, y + 0.16, marker="^", color=ORANGE, label="chat format (standard practice)")
ax.scatter(d_raw, y - 0.16, marker="o", color=BLUE, label="plain text (format held fixed)")
for i in range(len(fams6)):
    ax.plot([d_raw[i], d_chat[i]], [y[i] - 0.16, y[i] + 0.16], color=GRAY, lw=0.6, alpha=0.6)
ax.axvline(0, color="k", lw=0.8)
ax.set_yticks(y); ax.set_yticklabels(fams6)
ax.invert_yaxis()
ax.set_xlabel("caving change, base $\\rightarrow$ aligned")
ax.set_title("The apparent effect of alignment\ndepends on prompt format", fontsize=9)
ax.legend(frameon=False, fontsize=7, loc="lower left")
fig.savefig(f"{HERE}/fig_factorial.pdf")
plt.close(fig)

# ============================ APPENDIX FIG: MONITOR ============================
# detect artifacts, re-derived §64.1: gemma attendsX in-dist + held-out transfer vs difficulty;
# best-head transfer to four further models
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 2.6))
lab1 = ["in-distribution", "held-out:\ndistractor arg.", "held-out:\nspurious few-shot"]
att = [0.995, 0.998, 0.985]; diff = [0.706, 0.739, 0.787]
x = np.arange(3)
a1.bar(x - 0.18, att, width=0.36, color=BLUE, label="reader routing")
a1.bar(x + 0.18, diff, width=0.36, color=GRAY, label="difficulty baseline")
a1.axhline(0.5, color="k", lw=0.7, ls=":")
a1.set_xticks(x); a1.set_xticklabels(lab1, fontsize=7.5)
a1.set_ylabel("AUROC"); a1.set_ylim(0.4, 1.02)
a1.set_title("(a) Reader routing predicts caving\nbefore the answer (Gemma-2-2b)")
a1.legend(frameon=False, fontsize=7)
lab2 = ["gemma-9b", "olmo-7b", "qwen-7b", "tulu-sft"]
vals = [0.995, 0.954, 0.911, 0.970]
a2.bar(range(4), vals, color=GREEN, width=0.55)
a2.axhline(0.5, color="k", lw=0.7, ls=":")
a2.set_xticks(range(4)); a2.set_xticklabels(lab2, fontsize=7.5)
a2.set_ylim(0.4, 1.02); a2.set_ylabel("AUROC")
a2.set_title("(b) The same procedure transfers\nto four further models")
fig.tight_layout()
fig.savefig(f"{HERE}/fig_monitor.pdf")
plt.close(fig)

# ============================ APPENDIX FIG: COT INTERACTION (item-matched) ============================
# pooled over dpo+rlvr from cot_matched_tulu.json: items knew under BOTH answering modes
cm = json.load(open(f"{R}/cot_bridge/cot_matched_tulu.json"))["matched"]
def _pool(kind):
    n = d_ = c_ = 0
    for st_ in ("dpo", "rlvr"):
        cell = cm[f"{st_}_{kind}"]
        n += cell["n"]; d_ += cell["dir_cave"]; c_ += cell["cot_cave"]
    return d_ / n, c_ / n
k_dir, k_cot = _pool("bct")
a_dir, a_cot = _pool("arith")
z_cm = cm["pooled_interaction"]["z"]
fig, ax = plt.subplots(figsize=(3.6, 2.5))
x = np.arange(2)
ax.bar(x - 0.17, [k_dir, a_dir], width=0.34, color=GRAY, label="direct answer (MCQ)")
ax.bar(x + 0.17, [k_cot, a_cot], width=0.34, color=BLUE, label="reason first (CoT)")
ax.set_xticks(x); ax.set_xticklabels(["knowledge\n(retrieved)", "arithmetic\n(derivable)"])
ax.set_ylabel("caving rate (item-matched)")
ax.set_title(f"Reasoning first protects only answers\nthat can be re-derived ($z=+{z_cm:.1f}$)")
ax.legend(frameon=False, fontsize=7)
fig.savefig(f"{HERE}/fig_cot.pdf")
plt.close(fig)
print("new figures written")

# ============================ FIG 2 OVERLAY: API CELLS ============================
# regenerate the margin-law figure with API-model cells overlaid (§64.14; verdict: partial,
# within-model r<=-0.83 in 4/5, all cells inside the band)
cells = json.load(open(f"{R}/margin_race/margin_law_cells.json"))
api = json.load(open(f"{R}/api_law/api_cells.json"))
fig, ax = plt.subplots(figsize=(3.6, 2.7))
groups = {
    "graded / arithmetic ladders": (lambda l: l.startswith("cuestr"), BLUE, "o"),
    "published 4-cue grid": (lambda l: l.startswith("stage"), GREEN, "^"),
    "base vs tuned (native)": (lambda l: l.startswith("margin"), ORANGE, "s"),
}
for name, (sel, col, mk) in groups.items():
    g = [c for c in cells if sel(c["label"])]
    ax.scatter([c["race_p"] for c in g], [c["cave"] for c in g],
               s=13, alpha=0.5, color=col, marker=mk, label=f"{name} ({len(g)})", lw=0)
A = [c for c in api if c["n"] >= 15]
ax.scatter([c["margin"] for c in A], [c["cave"] for c in A],
           s=34, color="k", marker="*", label=f"API models ({len(A)} cells, 5 models)", zorder=4)
xs = [c["race_p"] for c in cells]; ys = [c["cave"] for c in cells]
mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
r = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / math.sqrt(
    sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
ax.text(0.03, 0.08, f"open-weight: n = {len(cells)}, r = {r:.2f}\nAPI cells: within band,\nwithin-model r $\\leq$ -0.83 (4/5)",
        transform=ax.transAxes, fontsize=7)
ax.set_xlabel("post-cue margin  $p(T)-p(X)$")
ax.set_ylabel("caving rate")
ax.set_title("The output-level collapse:\none curve across 207 conditions", fontsize=9)
ax.legend(frameon=False, loc="upper right", handletextpad=0.1, fontsize=6)
fig.savefig(f"{HERE}/fig2_marginlaw.pdf")
plt.close(fig)
print("fig2 overlay written")

# ============================ COMBINED: PHENOMENON + FORMAT (one caption) ============================
_saved = {k: plt.rcParams[k] for k in PAGE_RC}; plt.rcParams.update(PAGE_RC)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 2.42), gridspec_kw={"width_ratios": [1.4, 1]})
im = a1.imshow(M, cmap="Reds", vmin=0, vmax=1, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        a1.text(j, i, f"{M[i,j]*100:.0f}%", ha="center", va="center", fontsize=9.5,
                color="white" if M[i,j] > 0.55 else "black")
a1.set_xticks(range(4)); a1.set_xticklabels(CUELAB, fontsize=8)  # "commitment" is ~45pt wide on ~48pt centres
a1.set_yticks(range(len(FAMS))); a1.set_yticklabels([f[0] for f in FAMS])
a1.set_title("(a) Aligned models cave to all four cue types")
fig.colorbar(im, ax=a1, shrink=0.85, label="caving rate")
y = np.arange(len(fams6))
a2.scatter(d_chat, y + 0.16, marker="^", color=ORANGE, label="chat format")
a2.scatter(d_raw, y - 0.16, marker="o", color=BLUE, label="plain text")
for i in range(len(fams6)):
    a2.plot([d_raw[i], d_chat[i]], [y[i] - 0.16, y[i] + 0.16], color=GRAY, lw=0.6, alpha=0.6)
a2.axvline(0, ymax=6.0 / 7.1, color="k", lw=0.8)   # stop at the top data row, below the legend band
a2.set_yticks(y); a2.set_yticklabels(fams6)
a2.set_ylim(5.5, -1.6)   # inverted; the spare row above gemma-2b holds the legend, clear of any marker
a2.set_xlabel("caving change, base $\\rightarrow$ aligned")
a2.set_title("(b) The apparent alignment effect\ndepends on prompt format")
# a legend among scatter markers reads as more data points, so it sits in its own band at the top;
# "standard practice" / "format held fixed" are spelled out in the caption
a2.legend(frameon=False, loc="upper center", ncol=2, handletextpad=0.3, columnspacing=1.5, borderaxespad=0.15)
fig.tight_layout(w_pad=2.0)
fig.savefig(f"{HERE}/fig_phenom.pdf")
plt.close(fig)
plt.rcParams.update(_saved)

# ============================ COMBINED: LAW + DIAL (one caption) ============================
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.4, 2.78))
groups2 = {
    "graded / arithmetic ladders": (lambda l: l.startswith("cuestr"), BLUE, "o"),
    "published 4-cue grid": (lambda l: l.startswith("stage"), GREEN, "^"),
    "base vs tuned (native)": (lambda l: l.startswith("margin"), ORANGE, "s"),
}
for name, (sel, col, mk) in groups2.items():
    g = [c for c in cells if sel(c["label"])]
    a1.scatter([c["race_p"] for c in g], [c["cave"] for c in g],
               s=13, alpha=0.5, color=col, marker=mk, label=f"{name} ({len(g)})", lw=0)
A = [c for c in api if c["n"] >= 15]
a1.scatter([c["margin"] for c in A], [c["cave"] for c in A],
           s=34, color="k", marker="*", label=f"API models ({len(A)} cells, 5 models)", zorder=4)
a1.text(0.03, 0.06, f"open-weight: n = {len(cells)}, r = -0.93\nAPI cells: within band", transform=a1.transAxes, fontsize=7)
a1.set_xlabel("post-cue margin  $p(T)-p(X)$"); a1.set_ylabel("caving rate")
a1.set_title("(a) The output-level collapse:\none curve across 207 conditions", fontsize=9.5)
a1.legend(frameon=False, loc="upper right", handletextpad=0.1, fontsize=6.3)
cols = [GRAY, GREEN, BLUE, PURPLE, RED]
for (name, ys), c in zip(curves.items(), cols):
    a2.plot(range(len(lams)), ys, "o-", ms=3, lw=1.1, color=c, label=name)
a2.axhline(0.138, color="k", lw=0.7, ls=":")
a2.text(0.1, 0.10, "cue-free baseline (0.138)", fontsize=6.5)
a2.set_xticks(range(len(lams))); a2.set_xticklabels([str(l) for l in lams])
a2.set_xlabel(r"attention scale $\lambda$ on the cue span")
a2.set_ylabel("caving rate")
a2.set_title("(b) Attention scale $\\lambda$ controls caving\nsmoothly for every cue strength", fontsize=9.5)
a2.legend(frameon=False, loc="lower right", fontsize=6.3)
fig.tight_layout(w_pad=2.0)
fig.savefig(f"{HERE}/fig_lawdial.pdf")
plt.close(fig)
print("combined figures written")

# ============================ FIG: THE SWITCH (§4) ============================
# (a) gate_direction_llama_fromlog rows (verified §63.14): one instrument, one eval set
# (b) iclpatch artifacts (verified §63.13)
_saved = {k: plt.rcParams[k] for k in PAGE_RC}; plt.rcParams.update(PAGE_RC)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 2.24), gridspec_kw={"width_ratios": [1.2, 1]})
bars = [("base\n(untouched)", 0.21, GRAY), ("+ random\nvector", 0.22, GRAY),
        ("+ in-context\nshift $v_{icl}$", 0.65, ORANGE), ("+ SFT\nshift $v_{sft}$", 0.87, BLUE),
        ("SFT model\n(reference)", 0.78, "#7fb3d5")]
a1.bar(range(len(bars)), [b[1] for b in bars], color=[b[2] for b in bars], width=0.6)
for i, b in enumerate(bars):
    a1.text(i, b[1] + 0.02, f"{b[1]:.2f}", ha="center", fontsize=9.5)
a1.set_xticks(range(len(bars)))
a1.set_xticklabels([b[0] for b in bars], fontsize=8)  # five two-line labels on ~50pt centres
a1.set_ylabel("caving rate"); a1.set_ylim(0, 1.02)
a1.set_title("(a) Adding one activation direction to the base\ninstalls caving; random directions do not")
labels = ["readers\n+ writers", "writers", "readers", "random\nheads"]
g8 = [0.533, 0.475, 0.016, 0.024]   # 8 generic turns
m3 = [0.597, 0.543, 0.032, 0.008]   # 3 MCQ shots
x = np.arange(len(labels))
a2.bar(x - 0.18, g8, width=0.36, color=PURPLE, label="8 generic turns")
a2.bar(x + 0.18, m3, width=0.36, color=GREEN, label="3 MCQ shots")
a2.set_xticks(x); a2.set_xticklabels(labels)
a2.set_ylabel("flips recovered by patching"); a2.set_ylim(0, 0.75)
a2.set_title("(b) In-context activation runs through\nthe same circuit")
a2.legend(frameon=False, loc="upper right")
fig.tight_layout(w_pad=2.0)
fig.savefig(f"{HERE}/fig_switch.pdf")
plt.close(fig)
plt.rcParams.update(_saved)

# ============================ APPENDIX FIG: API SMALL MULTIPLES ============================
mods = {}
for c in api:
    if c["n"] >= 15: mods.setdefault(c["model"], []).append(c)
fig, axes = plt.subplots(1, 5, figsize=(10.5, 2.2), sharey=True)
for ax, (m, cs) in zip(axes, sorted(mods.items())):
    xs = [c["margin"] for c in cs]; ys = [c["cave"] for c in cs]
    ax.scatter(xs, ys, s=18, color=BLUE)
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    den = (sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys)) ** 0.5
    r = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / den if den else float("nan")
    ax.set_title(m.split("/")[-1][:20] + f"\nr = {r:+.2f}", fontsize=8)
    ax.set_xlabel("margin", fontsize=8)
axes[0].set_ylabel("caving rate")
fig.tight_layout()
fig.savefig(f"{HERE}/fig_api.pdf")
plt.close(fig)

# ============================ APPENDIX FIG: CONFIDENCE DISSOCIATION ============================
# analyze_cvb layer-mean table (verified this session): per model cell, flip-AUROC of the
# bias direction vs the confidence direction
cellsC = [("gemma base", .760, .376), ("gemma tuned", .774, .457), ("gemma9b base", .714, .466),
          ("gemma9b tuned", .789, .522), ("llama base", .838, .611), ("llama tuned", .875, .649),
          ("olmo base", .659, .460), ("olmo tuned", .817, .415), ("qwen14b base", .750, .405),
          ("qwen14b tuned", .647, .352), ("qwen7b base", .768, .510), ("qwen7b tuned", .602, .476)]
fig, ax = plt.subplots(figsize=(5.6, 2.6))
x = np.arange(len(cellsC))
ax.scatter(x, [c[1] for c in cellsC], color=BLUE, s=20, label="bias direction")
ax.scatter(x, [c[2] for c in cellsC], color=GRAY, s=20, label="confidence direction")
for i, c in enumerate(cellsC):
    ax.plot([i, i], [c[2], c[1]], color=GRAY, lw=0.7, alpha=0.6)
ax.axhline(0.5, color="k", lw=0.7, ls=":")
ax.text(0.1, 0.515, "chance", fontsize=6.5)
ax.set_xticks(x); ax.set_xticklabels([c[0] for c in cellsC], rotation=45, ha="right", fontsize=7)
ax.set_ylabel("flip-prediction AUROC")
ax.set_title("The bias direction predicts caving; the confidence direction does not (12 of 12 cells)", fontsize=9)
ax.legend(frameon=False, fontsize=7)
fig.savefig(f"{HERE}/fig_conf.pdf")
plt.close(fig)
print("three new figures written")

# ============================ FIG 1 (NEW): STANDALONE CONCEPT HERO ============================
fig, axs = plt.subplots(figsize=(10.2, 3.1))
axs.set_xlim(0, 20); axs.set_ylim(0, 6.2); axs.axis("off")

def box(x, y, w, h, fc, ec, lw=1.2):
    axs.add_patch(mp.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.07", fc=fc, ec=ec, lw=lw))

def chip(x, y, text, fc, tc):
    axs.add_patch(mp.FancyBboxPatch((x, y), 1.9, 0.42, boxstyle="round,pad=0.04", fc=fc, ec="none"))
    axs.text(x + 0.95, y + 0.21, text, ha="center", va="center", fontsize=6.4,
             color=tc, fontweight="bold")

# ---- row 1: the inversion ----
chip(0.2, 5.55, "STANDARD ACCOUNT", "#eeeeee", "#666666")
box(0.2, 4.35, 8.2, 1.0, "#f7f7f7", "#bbbbbb")
axs.text(4.3, 4.85, "preference training $teaches$ models to please,\nso sycophancy can be untaught",
         ha="center", va="center", fontsize=7.8, color="#666666")
axs.plot([0.7, 7.9], [4.42, 5.3], color=RED, lw=1.6, alpha=0.75)
axs.annotate("", xy=(9.6, 4.85), xytext=(8.65, 4.85), arrowprops=dict(arrowstyle="->", color="k", lw=1.3))
chip(9.8, 5.55, "THIS PAPER", "#e8f0e9", "#1e6b30")
box(9.8, 4.35, 10.0, 1.0, "white", GREEN, lw=1.4)
axs.text(14.8, 4.85, "nothing is taught: a pretrained circuit is activated by assistant context,\nand every recipe then sets its gain",
         ha="center", va="center", fontsize=7.8)

# ---- row 2: the mechanism timeline ----
stages = [
    (0.2, "#eef3fa", BLUE, "PRETRAINING", "the circuit is built:\nreaders find the cued\nanswer, writers copy it"),
    (5.25, "#fdf3e7", ORANGE, "FIRST ASSISTANT DATA", "the switch: ~200 generic\nexamples, or 8 in-context\nturns, activate it"),
    (10.3, "#f3eefa", PURPLE, "EVERY LATER STAGE", "the gain: RL turns it up,\nother recipes turn it down,\nconfidence never moves"),
    (15.35, "#fdf0f0", RED, "BEHAVIOR", "one law: caving tracks the\nmargin left after the cue\n($r=-0.93$, 207 conditions)"),
]
for i, (x, fc, ec, head, body) in enumerate(stages):
    box(x, 0.55, 4.45, 2.9, fc, ec)
    axs.text(x + 2.22, 3.0, head, ha="center", va="center", fontsize=7.6, fontweight="bold", color=ec)
    axs.text(x + 2.22, 1.65, body, ha="center", va="center", fontsize=7.2)
    if i < 3:
        axs.annotate("", xy=(x + 5.15, 2.0), xytext=(x + 4.6, 2.0),
                     arrowprops=dict(arrowstyle="->", color="k", lw=1.4))
# motifs: circuit dots / switch / dial / curve
axs.scatter([1.5, 2.2], [2.45, 2.45], s=32, color=BLUE)
axs.annotate("", xy=(2.13, 2.45), xytext=(1.58, 2.45), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.0))
axs.text(2.95, 2.42, "$\\rightarrow$ answer", fontsize=6.0, color=BLUE, va="center")
sw = mp.FancyBboxPatch((7.0, 2.28), 0.95, 0.36, boxstyle="round,pad=0.03", fc="white", ec=ORANGE)
axs.add_patch(sw); axs.add_patch(mp.Ellipse((7.75, 2.46), 0.30, 0.30, fc=ORANGE, ec="none"))
axs.text(8.15, 2.46, "ON", fontsize=6.0, color=ORANGE, va="center")
axs.add_patch(mp.Ellipse((12.5, 2.46), 0.42, 0.42, fc="white", ec=PURPLE, lw=1.2))
axs.plot([12.5, 12.66], [2.46, 2.62], color=PURPLE, lw=1.6)
axs.annotate("", xy=(13.1, 2.72), xytext=(12.95, 2.30),
             arrowprops=dict(arrowstyle="->", color=PURPLE, lw=0.9,
                             connectionstyle="arc3,rad=-0.4"))
axs.annotate("", xy=(11.9, 2.26), xytext=(12.05, 2.68),
             arrowprops=dict(arrowstyle="->", color=PURPLE, lw=0.9,
                             connectionstyle="arc3,rad=-0.4"))
import numpy as _np
cx = _np.linspace(16.4, 18.9, 40)
cy = 2.25 + 0.45 / (1 + _np.exp((cx - 17.65) * 4))
axs.plot(cx, cy, color=RED, lw=1.4)
fig.savefig(f"{HERE}/fig_concept.pdf")
plt.close(fig)

# ============================ FIG 2 (NEW): EVIDENCE PANELS (hero minus strip) ============================
# Placed at \linewidth (5.5in) from an 8.0in canvas, so in-figure sizes scale by 0.69 on the page:
# 11pt titles/labels -> 7.6pt, 10pt ticks -> 6.9pt, 9.5pt annotations -> 6.5pt. Scoped to this figure.
_ev_saved = {k: plt.rcParams[k] for k in PAGE_RC}
plt.rcParams.update(PAGE_RC)
YT = [0, 0.25, 0.5, 0.75, 1.0]  # 0.2 steps crowded the y axis at page scale
fig, axes3 = plt.subplots(1, 3, figsize=(8.0, 3.1), gridspec_kw={"width_ratios": [1, 1.22, 1]})
ax = axes3[0]
labels = ["no swap", "+readers", "+writers", "+full circuit"]
base_arm = [0.215, 0.215, 0.210, 0.217]; tuned_arm = [0.802, 0.812, 0.810, 0.810]
x = range(4)
ax.bar([i - 0.19 for i in x], base_arm, width=0.38, color=GRAY, label="pretrained base")
ax.bar([i + 0.19 for i in x], tuned_arm, width=0.38, color=BLUE, label="aligned model")
ax.set_xticks(list(x))
ax.set_xticklabels(labels, rotation=30, ha="right", rotation_mode="anchor")  # 15deg let neighbours overlap
ax.set_xlabel("circuit weights swapped in")
ax.set_ylabel("caving rate"); ax.set_ylim(0, 1.22); ax.set_yticks(YT)
ax.set_title("(a) Swapping circuit weights\nbetween base and aligned\nmodels changes nothing")
ax.legend(frameon=False, loc="upper left", handlelength=1.2, borderaxespad=0.3)
ax = axes3[1]
ns = [20, 50, 200, 939000]
attx = [0.000, 0.363, 0.695, 0.57]; cave = [0.37, 0.91, 0.94, 0.78]
ax.plot(ns, attx, "o-", color=ORANGE)
ax.plot(ns, cave, "s-", color=PURPLE)
ax.scatter([8], [0.42], marker="o", facecolor="white", edgecolor=ORANGE, zorder=4)
ax.scatter([8], [0.693], marker="s", facecolor="white", edgecolor=PURPLE, zorder=4)
ax.text(500, 0.975, "caving rate", color=PURPLE, fontsize=9.5, ha="left", va="bottom")
ax.text(1.25e6, 0.50, "reader routing\nto cue", color=ORANGE, fontsize=9.5, ha="right", va="top")
ax.axhline(0.21, color=GRAY, lw=0.8, ls=":")
ax.text(1.25e6, 0.185, "base caving", color=GRAY, fontsize=9.5, ha="right", va="top")
ax.set_xscale("log"); ax.set_xlim(4.5, 1.35e6)
ax.set_xticks([8, 50, 200, 939000])
ax.set_xticklabels(["8\n(in-ctx)", "50", "200", "full SFT\n(939k)"], fontsize=9.5)
ax.get_xticklabels()[1].set_ha("right")  # 50 and 200 are 17pt apart on this log axis; keep them from touching
ax.set_xlabel("generic, cue-free\nassistant examples"); ax.set_ylim(0, 1.12); ax.set_yticks(YT)
ax.set_title("(b) About 200 generic\nassistant examples\nactivate the circuit")
ax = axes3[2]
pts = json.load(open(f"{R}/stagewise/fingerprint.json"))["points"]
xs = [p["att"] for p in pts]; ys = [p["cave"] for p in pts]
mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
r = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / math.sqrt(
    sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
for p in pts:
    c = GRAY if p["stage"] == "base" else BLUE
    ax.scatter(p["att"], p["cave"], s=30, color=c, zorder=3)
beta = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / sum((a-mx)**2 for a in xs)
xr = [min(xs), max(xs)]
ax.plot(xr, [my + beta*(v-mx) for v in xr], color=RED, lw=1, alpha=0.7)
# colour-matched text labels instead of a legend: legend markers among scatter points read as extra data
ax.text(0.24, 0.11, "base checkpoints", color="#707070", fontsize=9, ha="left", va="center")
ax.text(0.40, 0.31, "tuned checkpoints", color=BLUE, fontsize=9, ha="left", va="center")
ax.text(0.05, 0.9, f"r = {r:.2f}", transform=ax.transAxes, color=RED)
ax.set_xlabel("reader routing rate\ntoward the cued answer"); ax.set_ylabel("caving rate")
ax.set_xlim(0, 1.0); ax.set_ylim(0, 1.08); ax.set_yticks(YT)
ax.set_title(f"(c) Reader routing predicts\ncaving across {len(pts)} checkpoints")
fig.tight_layout(w_pad=1.5)
fig.savefig(f"{HERE}/fig_evidence.pdf")
plt.close(fig)
plt.rcParams.update(_ev_saved)
print("concept + evidence written")

# ============================ FIG 1 v3: HOUSE-STYLE CONCEPT HERO ============================
fig, axs = plt.subplots(figsize=(10.2, 3.6))
axs.set_xlim(0, 20); axs.set_ylim(0, 7.2); axs.axis("off")

def box(x, y, w, h, fc, ec, lw=1.1):
    axs.add_patch(mp.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06", fc=fc, ec=ec, lw=lw))

# ---- header strip: the inversion (single centered lines) ----
box(0.15, 6.15, 9.2, 0.8, "#f7f7f7", "#bbbbbb")
axs.text(4.75, 6.55, "Standard account: preference training teaches sycophancy  $\\times$",
         fontsize=7.6, ha="center", va="center", color="#666666")
axs.annotate("", xy=(10.3, 6.55), xytext=(9.55, 6.55), arrowprops=dict(arrowstyle="->", color="k", lw=1.2))
box(10.45, 6.15, 9.4, 0.8, "#eef7ef", "#2e8b46", lw=1.3)
axs.text(15.15, 6.55, "This paper: nothing is taught; a pretrained circuit is activated, its gain set",
         fontsize=7.3, ha="center", va="center", color="#1e4d2b")

# ---- numbered stage headers, anchored to their boxes ----
heads = [(0.15, BLUE, "1. Pretraining builds it"),
         (5.0, ORANGE, "2. Assistant context activates it"),
         (11.3, PURPLE, "3. Training sets the gain"),
         (15.75, RED, "4. One law for behavior")]
for x, c, t in heads:
    axs.text(x + 0.1, 5.5, t, fontsize=7.8, fontweight="bold", color=c)

# ---- stage 1 ----
box(0.15, 0.5, 4.45, 4.6, "#f4f8fd", BLUE)
axs.text(2.37, 4.45, "readers attend to a cued\noption; writers copy it", ha="center", fontsize=6.9)
axs.scatter([1.35, 2.35], [3.2, 3.2], s=110, color=BLUE, zorder=3)
axs.text(1.35, 3.2, "R", ha="center", va="center", fontsize=7, color="white", zorder=4)
axs.text(2.35, 3.2, "W", ha="center", va="center", fontsize=7, color="white", zorder=4)
axs.annotate("", xy=(2.12, 3.2), xytext=(1.58, 3.2), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.3))
axs.annotate("", xy=(3.45, 3.2), xytext=(2.58, 3.2), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.3))
axs.text(3.55, 3.2, "ans.", fontsize=6.6, color=BLUE, va="center")
axs.text(2.37, 1.5, "same weights before and\nafter alignment: transplants\nchange nothing", ha="center", fontsize=6.6, color="#455a74")

# ---- stage 2: activation, concrete example ----
box(5.0, 0.5, 6.1, 4.6, "#fdf8f0", ORANGE)
box(5.25, 2.75, 3.35, 1.95, "white", "#c9a468", lw=0.9)
axs.text(5.45, 4.35, "Which planet is largest?", fontsize=6.5)
axs.text(5.45, 3.9, "(A) Jupiter   (B) Mars", fontsize=6.5)
axs.text(5.45, 3.35, "I think the answer is (B).", fontsize=6.5, color=RED, style="italic")
box(8.85, 3.6, 2.05, 1.05, "#f2f2f2", "#999999", lw=0.9)
axs.text(9.87, 4.38, "base (circuit idle)", fontsize=5.9, ha="center", color="#666666")
axs.text(9.87, 3.95, "``(A) Jupiter''  $\\checkmark$", fontsize=6.8, ha="center")
box(8.85, 2.25, 2.05, 1.05, "#eef3fa", BLUE, lw=0.9)
axs.text(9.87, 3.03, "assistant (circuit active)", fontsize=5.9, ha="center", color=BLUE)
axs.text(9.87, 2.6, "``(B) Mars''  $\\times$", fontsize=6.8, ha="center", color=RED)
axs.annotate("", xy=(8.78, 4.1), xytext=(8.62, 3.85), arrowprops=dict(arrowstyle="->", color="#999999", lw=1.0))
axs.annotate("", xy=(8.78, 2.8), xytext=(8.62, 3.3), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.0))
axs.text(8.05, 1.3, "the switch: ~200 generic examples, even\npure code, or 8 in-context turns;\nno sycophancy-related data needed", ha="center", fontsize=6.5, color="#455a74")

# ---- stage 3 ----
box(11.3, 0.5, 4.15, 4.6, "#f7f3fb", PURPLE)
axs.add_patch(mp.Ellipse((13.37, 3.45), 1.15, 1.15, fc="white", ec=PURPLE, lw=1.4))
axs.plot([13.37, 13.78], [3.45, 3.86], color=PURPLE, lw=2)
axs.text(13.37, 2.45, "RLVR turns it up,\nother recipes turn it down", ha="center", fontsize=6.6, color=PURPLE)
axs.text(13.37, 1.3, "12 of 13 preregistered tests;\nconfidence never rises", ha="center", fontsize=6.5, color="#455a74")

# ---- stage 4 ----
box(15.75, 0.5, 4.1, 4.6, "#fdf2f2", RED)
import numpy as _np
cx = _np.linspace(16.35, 19.35, 50)
cy = 2.15 + 1.75 / (1 + _np.exp((cx - 17.85) * 3.2))
axs.plot(cx, cy, color=RED, lw=1.5)
axs.annotate("margin after cue", xy=(17.85, 1.7), fontsize=6.2, ha="center")
axs.text(16.12, 3.0, "caving", fontsize=6.2, rotation=90, va="center")
axs.text(17.8, 4.45, "$r=-0.93$ over 207 conditions;\nreadable before the answer,\nsettable with one scalar", ha="center", fontsize=6.5, color="#455a74")
fig.savefig(f"{HERE}/fig_concept.pdf")
plt.close(fig)
print("concept v3 written")

# ============================ FIG 6 v3 (round-2 feedback): MATCHING BARS + DIAL ============================
# (a) gain-matching absolute susceptibilities (matched-known sets, 2000-boot CIs,
#     results/gain_match/gainmatch_abs_matched.json re-derived from per-item rows §66.5)
# (b) dial curves (unchanged). The 207-cell margin scatter moves to the appendix
#     (fig2_marginlaw.pdf, written above).
gm = json.load(open(f"{R}/gain_match/gainmatch_abs_matched.json"))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.4, 3.0))
arm_order = ["dpo@1", "dpo@up", "rl@down", "rl@1"]
arm_lab = ["DPO", "DPO\n@$\\lambda_\\uparrow$", "RL\n@$\\lambda_\\downarrow$", "RL"]
arm_col = [GRAY, "#7f9fc4", "#b9c8d8", BLUE]
Ms = {"tulu": ("$M_\\uparrow{=}0.80$", "$M_\\downarrow{=}0.51$"),
      "olmo": ("$M_\\uparrow{=}1.23$", "$M_\\downarrow{=}1.39$")}
for gi, (lin, nlab) in enumerate([("tulu", "Tulu (DPO$\\to$RLVR)"), ("olmo", "OLMo (DPO$\\to$Instruct)")]):
    xs = [gi * 5 + k for k in range(4)]
    for k, arm in enumerate(arm_order):
        v = gm[lin][arm]
        a1.bar(xs[k], v["point"], width=0.8, color=arm_col[k],
               yerr=[[v["point"] - v["ci95"][0]], [v["ci95"][1] - v["point"]]],
               error_kw=dict(lw=0.9), capsize=2)
    a1.plot([xs[0] - 0.45, xs[3] + 0.45], [gm[lin]["dpo@1"]["point"]] * 2, ls=":", lw=0.8, color=GRAY)
    a1.plot([xs[0] - 0.45, xs[3] + 0.45], [gm[lin]["rl@1"]["point"]] * 2, ls=":", lw=0.8, color=BLUE)
    top = max(gm[lin][a]["ci95"][1] for a in arm_order)
    a1.text(xs[1], top + 0.025, Ms[lin][0], ha="center", fontsize=6.6)
    a1.text(xs[2], top + 0.085, Ms[lin][1], ha="center", fontsize=6.6)
    a1.text(xs[1] + 0.5, -0.135, nlab, ha="center", fontsize=7.5)
    for k in range(4):
        a1.text(xs[k], -0.06, arm_lab[k], ha="center", fontsize=6.4)
a1.set_xticks([])
a1.set_ylim(0, 0.85)
a1.set_ylabel("susceptibility $\\Delta p_X$ (matched items)")
a1.set_title("(a) Attention matched to the other stage's level\ntransfers the stage difference in susceptibility", fontsize=9.5)
cols = [GRAY, GREEN, BLUE, PURPLE, RED]
for (name, ys), c in zip(curves.items(), cols):
    a2.plot(range(len(lams)), ys, "o-", ms=3, lw=1.1, color=c, label=name)
a2.axhline(0.138, color="k", lw=0.7, ls=":")
a2.text(0.1, 0.10, "cue-free baseline (0.138)", fontsize=6.5)
a2.set_xticks(range(len(lams))); a2.set_xticklabels([str(l) for l in lams])
a2.set_xlabel(r"attention scale $\lambda$ on the cue span")
a2.set_ylabel("caving rate")
a2.set_title("(b) Attention scale $\\lambda$ controls caving\nsmoothly for every cue strength", fontsize=9.5)
a2.legend(frameon=False, loc="lower right", fontsize=6.3)
fig.tight_layout(w_pad=2.0)
fig.savefig(f"{HERE}/fig_lawdial.pdf")
plt.close(fig)
print("fig6 v3 written")

# ============================ FIG 6 v5 (round-6): NATURAL INTERCHANGE + SCOPE FOREST + DIAL ============================
# (a) natural carrier-band interchange raw susceptibilities (interchange_{lin}.json ABS
#     summaries, verified §68.6/§69.5). (b) M by scope (values verified §67.3/§69.2).
# (c) dial curves. Lambda matching bars (network + band) live in fig_gainmatch_bars.pdf.
gc = json.load(open(f"{R}/gain_local/gainlocal_carrier_abs.json"))
ic = {lin: json.load(open(f"{R}/interchange/interchange_{lin}.json")) for lin in ("tulu", "olmo")}
_saved = {k: plt.rcParams[k] for k in PAGE_RC}; plt.rcParams.update(PAGE_RC)
# 8.6in canvas (page scale 0.64): (a) needs ~13pt per bar for vertical labels, and (b)/(c) carry wide row labels
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(8.6, 2.98), gridspec_kw={"width_ratios": [1.25, 1.25, 1]})
arm_order = ["dpo@1", "dpo@up", "rl@down", "rl@1"]
arm_lab = ["DPO", "DPO\u2191", "RL\u2193", "RL"]   # plain-text arrows: mathtext adds a thin space that costs ~4pt per label
arm_col = [GRAY, "#7f9fc4", "#b9c8d8", BLUE]
Mc = {"tulu": ("0.99", "0.97"), "olmo": ("0.92", "0.75")}
ic_arms = ["dpo@1", "dpo@carrier", "rl@carrier", "rl@1"]
Mi = {"tulu": ("0.73", "0.72"), "olmo": ("0.62", "0.61")}   # (up, down), verified §68.6
for gi, (lin, nlab) in enumerate([("tulu", "Tulu"), ("olmo", "OLMo")]):
    xs = [gi * 5 + k for k in range(4)]
    A = {a: ic[lin]["held"][a + "_summary"]["susc_matched"] for a in ic_arms}
    for k, arm in enumerate(ic_arms):
        v = A[arm]
        a1.bar(xs[k], v["point"], width=0.8, color=arm_col[k],
               yerr=[[v["point"] - v["ci95"][0]], [v["ci95"][1] - v["point"]]],
               error_kw=dict(lw=1.1), capsize=2.5)
    a1.plot([xs[0] - 0.45, xs[3] + 0.45], [A["dpo@1"]["point"]] * 2, ls=":", lw=0.8, color=GRAY)
    a1.plot([xs[0] - 0.45, xs[3] + 0.45], [A["rl@1"]["point"]] * 2, ls=":", lw=0.8, color=BLUE)
    top = max(A[a]["ci95"][1] for a in ic_arms)
    a1.text(xs[1] + 0.5, top + 0.10, f"$M_\\uparrow{{=}}${Mi[lin][0]}", ha="center", fontsize=8)
    a1.text(xs[1] + 0.5, top + 0.025, f"$M_\\downarrow{{=}}${Mi[lin][1]}", ha="center", fontsize=8)
    # point offset (not axes fraction): tight_layout measures it once, so it must not scale with axes height
    a1.annotate(nlab, xy=(xs[1] + 0.5, 0), xycoords=("data", "axes fraction"), xytext=(0, -32),
                textcoords="offset points", ha="center", va="top", fontsize=10)
# arm labels as vertical tick labels: bars are ~11pt apart, which fits 8.5pt text only when rotated 90 degrees.
# The arrow notation matches the M_up / M_down annotations.
a1.set_xticks([gi * 5 + k for gi in range(2) for k in range(4)])
a1.set_xticklabels([lab for gi in range(2) for lab in arm_lab], fontsize=8.5, rotation=90)
a1.tick_params(axis="x", length=0)
a1.set_xlim(-0.6, 8.6)
a1.set_ylim(0, 0.92)
a1.set_ylabel("susceptibility\n$\\Delta p_X$")
a1.set_title("(a) Swapping the checkpoints'\nown attention patterns\ntransfers the stage difference")
# (b) qkv decomposition forest (live from interchange_qkv artifacts, §71.2-verified)
iq = {lin: json.load(open(f"{R}/interchange/interchange_qkv_{lin}.json")) for lin in ("tulu", "olmo")}
qrows = [("q + k\n(= pattern)", "qk"), ("query only", "qside"), ("key only", "kside"), ("value only", "vside")]
qys = list(range(len(qrows)))[::-1]
for y, (lab, arm) in zip(qys, qrows):
    if arm == "qside":
        a2.axhspan(y - 0.42, y + 0.42, color="#fff3d6", zorder=0)
    for lin, mk, col, dys in (("tulu", "o", BLUE, (0.17, 0.05)), ("olmo", "^", ORANGE, (-0.07, -0.19))):
        for kind, dy in zip(("down", "up"), dys):
            r = iq[lin][f"M_{kind}_{arm}"]
            filled = kind == "down"
            a2.errorbar(r["point"], y + dy, xerr=[[r["point"] - r["ci95"][0]], [r["ci95"][1] - r["point"]]],
                        fmt=mk, ms=5.0, color=col, mfc=col if filled else "white",
                        mew=1.1, elinewidth=0.9, capsize=2)
a2.axvline(0, color="k", lw=0.7)
a2.axvline(1, color="k", lw=0.5, ls=":")
a2.set_yticks(qys); a2.set_yticklabels([r[0] for r in qrows])
a2.set_xlabel("mediated fraction $M$\nof the stage difference")
a2.set_title("(b) Query states carry the\nlargest single share of\nthe stage difference")
from matplotlib.lines import Line2D
# filled/open (down/up) is spelled out in the caption; the long label collided with the value-only row
a2.legend(handles=[
    Line2D([], [], marker="o", color=BLUE, ls="", ms=5, label="Tulu"),
    Line2D([], [], marker="^", color=ORANGE, ls="", ms=5, label="OLMo")],
    frameon=False, loc="lower right")
# (c) lambda-scope forest
NM = "nm"  # cannot match / lambda=1 sentinel; None = not run (no marker)
rows = [
    ("network-wide", 0.51, 0.80, 1.39, 1.23),
    ("carrier band", 0.97, 0.99, 0.75, 0.92),
    ("reader layers", 0.06, 0.03, 0.69, 0.69),
    ("R+W heads", 0.09, 0.12, None, None),
    ("reader heads", -0.06, -0.07, 0.40, 0.42),
    ("low band", NM, NM, 0.09, NM),
    ("high band", NM, NM, NM, NM),
    ("random 6L (a)", NM, NM, -0.01, NM),
    ("random 6L (b)", NM, NM, 0.03, NM),
]
ys = list(range(len(rows)))[::-1]
for y, (lab, td, tu_, od, ou) in zip(ys, rows):
    if lab == "carrier band":
        a3.axhspan(y - 0.42, y + 0.42, color="#fff3d6", zorder=0)
    for v, mk, col, dy in [(td, "o", BLUE, 0.17), (tu_, "o", BLUE, 0.05), (od, "^", ORANGE, -0.07), (ou, "^", ORANGE, -0.19)]:
        if v is None:
            continue
        if v == "nm":
            a3.plot(0, y + dy, marker="x", color=GRAY, ms=4.5, mew=1.2)
        else:
            filled = dy in (0.17, -0.07)
            a3.plot(v, y + dy, marker=mk, ms=5.0, color=col,
                    mfc=col if filled else "white", mew=1.1)
a3.axvline(0, color="k", lw=0.7)
a3.axvline(1, color="k", lw=0.5, ls=":")
a3.set_yticks(ys); a3.set_yticklabels([r[0] for r in rows], fontsize=9)  # nine rows on ~9.5pt centres
a3.set_xlabel("mediated fraction $M$")
a3.set_title("(c) The gain localizes to\nthe band directly below\nthe reader heads")
# the x marker (cannot match / lambda=1) is explained in the caption; (c) has no marker-free corner for a legend
fig.tight_layout(w_pad=1.6, rect=(0.015, 0.01, 0.985, 1.0))
fig.savefig(f"{HERE}/fig_lawdial.pdf")
plt.close(fig)
plt.rcParams.update(_saved)

# appendix: dial curves (moved out of fig6 in round 8)
fig, axd = plt.subplots(figsize=(4.4, 2.6))
cols = [GRAY, GREEN, BLUE, PURPLE, RED]
for (name, ys_), c in zip(curves.items(), cols):
    axd.plot(range(len(lams)), ys_, "o-", ms=2.6, lw=1.0, color=c, label=name)
axd.axhline(0.138, color="k", lw=0.7, ls=":")
axd.set_xticks(range(len(lams))); axd.set_xticklabels([str(l) for l in lams], fontsize=7.5)
axd.set_xlabel(r"attention scale $\lambda$ on the cue span")
axd.set_ylabel("caving rate")
axd.legend(frameon=False, loc="lower right", fontsize=6.2)
fig.tight_layout()
fig.savefig(f"{HERE}/fig_dialcurves.pdf")
plt.close(fig)

# appendix: global matching bars (previously fig6a)
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(8.8, 2.9))
for panel, src in ((ax, gm), (ax2, gc)):
    for gi, (lin, nlab) in enumerate([("tulu", "Tulu (DPO$\\to$RLVR)"), ("olmo", "OLMo (DPO$\\to$Instruct)")]):
        xs = [gi * 5 + k for k in range(4)]
        for k, arm in enumerate(arm_order):
            v = src[lin][arm]
            panel.bar(xs[k], v["point"], width=0.8, color=arm_col[k],
                      yerr=[[v["point"] - v["ci95"][0]], [v["ci95"][1] - v["point"]]],
                      error_kw=dict(lw=0.9), capsize=2)
        panel.plot([xs[0] - 0.45, xs[3] + 0.45], [src[lin]["dpo@1"]["point"]] * 2, ls=":", lw=0.8, color=GRAY)
        panel.plot([xs[0] - 0.45, xs[3] + 0.45], [src[lin]["rl@1"]["point"]] * 2, ls=":", lw=0.8, color=BLUE)
        panel.text(xs[1] + 0.5, -0.14, nlab, ha="center", fontsize=7)
        for k in range(4):
            panel.text(xs[k], -0.065, arm_lab[k], ha="center", fontsize=6.2)
    panel.set_xticks([]); panel.set_ylim(0, 0.85)
ax.set_ylabel("susceptibility $\\Delta p_X$ (matched items)")
ax.set_title("(a) Network-wide attention matching\ntransfers the stage difference", fontsize=9)
ax2.set_title("(b) Matching only in the carrier band\nlands on the other stage's level", fontsize=9)
fig.tight_layout()
fig.savefig(f"{HERE}/fig_gainmatch_bars.pdf")
plt.close(fig)
print("fig6 v4 + appendix bars written")
