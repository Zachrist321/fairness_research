"""
Generate polished publication-quality figures for the stereotype research paper.
Saves all figures to research_experiment/figures/
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np

OUTPUT_DIR = "/Users/zach/python/fairness_research/research_experiment/figures"

# ─── Shared style ────────────────────────────────────────────────────────────
PALETTE = {
    "implicit": "#2E86AB",   # deep blue
    "semi":     "#E84855",   # vivid red
    "llama":    "#4C72B0",
    "mistral":  "#DD4444",
    "qwen":     "#2CA02C",
    "female":   "#C2185B",
    "male":     "#1565C0",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
})


# ─── Figure 1: Joint effect interaction plot ─────────────────────────────────
def fig1_joint_effect():
    conditions = ["T=0.3\np=1.0", "T=1.0\np=0.3", "T=1.0\np=0.9", "T=1.5\np=1.0"]
    implicit   = [56.25, 55.0,  62.96, 61.25]
    semi       = [58.75, 63.64, 58.75, 53.95]

    x = np.arange(len(conditions))
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(x, implicit, marker="o", markersize=9, linewidth=2.5,
            color=PALETTE["implicit"], label="Implicit prompts", zorder=3)
    ax.plot(x, semi, marker="s", markersize=9, linewidth=2.5,
            color=PALETTE["semi"], label="Semi-explicit prompts", zorder=3)

    for xi, (iv, sv) in enumerate(zip(implicit, semi)):
        ax.annotate(f"{iv:.0f}%", (xi, iv), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=10,
                    color=PALETTE["implicit"], fontweight="bold")
        ax.annotate(f"{sv:.0f}%", (xi, sv), textcoords="offset points",
                    xytext=(0, -16), ha="center", fontsize=10,
                    color=PALETTE["semi"], fontweight="bold")

    ax.axhline(50, color="gray", linestyle="--", linewidth=1, alpha=0.6, label="50% chance")
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=10)
    ax.set_ylim(40, 75)
    ax.set_xlabel("Inference hyperparameter condition")
    ax.set_ylabel("Stereotype-aligned protagonist (%)")
    ax.set_title("Joint effect: prompt specificity × inference hyperparameters\n"
                 "(χ²=2.95, df=7, p=0.889 — interaction not significant)")
    ax.legend(frameon=True, framealpha=0.9, loc="upper right")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%g%%"))
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/fig1_joint_effect_interaction.png")
    plt.close(fig)
    print("Saved fig1_joint_effect_interaction.png")


# ─── Figure 2: Joint effect stratified by model (heatmaps) ───────────────────
def fig2_joint_effect_by_model():
    models = ["Llama 3.1 8B", "Mistral 7B", "Qwen 2.5 7B"]
    tiers  = ["Implicit", "Semi"]
    conds  = ["T=0.3\np=1.0", "T=1.0\np=0.3", "T=1.0\np=0.9", "T=1.5\np=1.0"]

    # rows = tiers (implicit, semi), cols = conditions
    data = {
        "Llama 3.1 8B":  np.array([[48, 58, 63, 59],
                                    [52, 56, 50, 46]]),
        "Mistral 7B":    np.array([[63, 63, 78, 74],
                                    [69, 72, 70, 67]]),
        "Qwen 2.5 7B":   np.array([[58, 44, 48, 50],
                                    [56, 64, 56, 50]]),
    }

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    fig.suptitle("Joint effect by model: tier × condition (%)",
                 fontsize=14, fontweight="bold", y=1.02)

    for ax, (model_name, mat) in zip(axes, data.items()):
        im = ax.imshow(mat, cmap="YlOrRd", vmin=40, vmax=85, aspect="auto")
        ax.set_xticks(range(4))
        ax.set_xticklabels(conds, fontsize=8.5)
        ax.set_yticks(range(2))
        ax.set_yticklabels(tiers, fontsize=10)
        ax.set_title(model_name, fontsize=12, fontweight="bold")
        for r in range(2):
            for c in range(4):
                val = mat[r, c]
                color = "white" if val > 65 else "black"
                ax.text(c, r, f"{val}%", ha="center", va="center",
                        fontsize=10, fontweight="bold", color=color)

    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.85, label="Stereotype-aligned (%)")
    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/fig2_joint_effect_by_model.png")
    plt.close(fig)
    print("Saved fig2_joint_effect_by_model.png")


# ─── Figure 3: Implicit defaults by role ─────────────────────────────────────
def fig3_role_defaults():
    roles = [
        "Nurse\n(female-stereotyped)",
        "Kindergarten teacher\n(female-stereotyped)",
        "Ballet dancer\n(female-stereotyped)",
        "Social worker\n(female-stereotyped)",
        "Surgeon\n(male-stereotyped)",
        "Mech. engineer\n(male-stereotyped)",
        "Software engineer\n(male-stereotyped)",
        "CEO\n(male-stereotyped)",
        "Military officer\n(male-stereotyped)",
    ]
    female = [100, 100, 100, 91.4, 80.6, 80.6, 76.5, 69.4, 55.6]
    male   = [0,   0,   0,   8.6,  19.4, 19.4, 23.5, 30.6, 44.4]

    y = np.arange(len(roles))
    fig, ax = plt.subplots(figsize=(9, 6))

    ax.barh(y, female, color=PALETTE["female"], label="Female-coded", alpha=0.88)
    ax.barh(y, male, left=female, color=PALETTE["male"], label="Male-coded", alpha=0.88)

    for i, (f, m) in enumerate(zip(female, male)):
        if f > 5:
            ax.text(f / 2, i, f"{f:.0f}%", ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")
        if m > 5:
            ax.text(f + m / 2, i, f"{m:.0f}%", ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")

    ax.axvline(50, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(roles, fontsize=9.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of generated protagonists (%)")
    ax.set_title("Protagonist gender in implicit role prompts\n"
                 "(no demographic identity specified in prompt)")
    ax.legend(loc="lower right", framealpha=0.9)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%g%%"))

    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/fig3_role_defaults.png")
    plt.close(fig)
    print("Saved fig3_role_defaults.png")


# ─── Figure 4: Model comparison bar chart ────────────────────────────────────
def fig4_model_comparison():
    models = ["Mistral 7B\nInstruct", "Llama 3.1 8B\nInstruct", "Qwen 2.5 7B\nInstruct"]
    rates  = [69.5, 54.0, 53.1]
    colors = [PALETTE["mistral"], PALETTE["llama"], PALETTE["qwen"]]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(models, rates, color=colors, width=0.5, edgecolor="white",
                  linewidth=1.5)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                f"{rate:.1f}%", ha="center", va="bottom",
                fontsize=12, fontweight="bold")

    ax.axhline(50, color="gray", linestyle="--", linewidth=1.2, alpha=0.7,
               label="50% (chance level)")
    ax.set_ylim(0, 85)
    ax.set_ylabel("Stereotype-aligned protagonist (%)")
    ax.set_title("Stereotype-aligned defaulting by model\n(implicit + semi-explicit prompts combined)")
    ax.legend(frameon=True, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%g%%"))
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/fig4_model_comparison.png")
    plt.close(fig)
    print("Saved fig4_model_comparison.png")


# ─── Figure 5: Tiered bias summary ───────────────────────────────────────────
def fig5_tiered_summary():
    tiers = ["Explicit bias\n(overt stereotype\nlanguage)",
             "Semi-explicit bias\n(neutral-name\nprompts)",
             "Implicit bias\n(role-only\nprompts)"]
    rates = [0.0, 58.8, 58.9]
    colors = ["#2ECC71", PALETTE["semi"], PALETTE["implicit"]]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(tiers, rates, color=colors, width=0.5, edgecolor="white", linewidth=1.5)

    for bar, rate in zip(bars, rates):
        label = f"{rate:.1f}%"
        ypos  = bar.get_height() + 1.2 if bar.get_height() < 80 else bar.get_height() - 5
        ax.text(bar.get_x() + bar.get_width() / 2, ypos,
                label, ha="center", va="bottom",
                fontsize=13, fontweight="bold")

    ax.axhline(50, color="gray", linestyle="--", linewidth=1.2, alpha=0.7, label="50% baseline")
    ax.set_ylim(0, 80)
    ax.set_ylabel("Bias-aligned rate (%)")
    ax.set_title("Stereotype-aligned rates by bias tier\n(gender dimension, 972 stories)")
    ax.legend(frameon=True, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%g%%"))
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/fig5_tiered_bias_summary.png")
    plt.close(fig)
    print("Saved fig5_tiered_bias_summary.png")


# ─── Figure 6: Hyperparameter effect ─────────────────────────────────────────
def fig6_hyperparameter_effect():
    conditions = ["T=0.3\np=1.0", "T=1.0\np=0.3", "T=1.0\np=0.9", "T=1.5\np=1.0"]
    rates      = [57.5, 59.2, 60.9, 57.7]

    x = np.arange(len(conditions))
    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.bar(x, rates, color="#7986CB", width=0.5, edgecolor="white", linewidth=1.5)
    for xi, r in enumerate(rates):
        ax.text(xi, r + 0.5, f"{r:.1f}%", ha="center", va="bottom",
                fontsize=11, fontweight="bold")

    ax.axhline(50, color="gray", linestyle="--", linewidth=1.2, alpha=0.7, label="50% baseline")
    ax.set_ylim(40, 75)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=10)
    ax.set_ylabel("Stereotype-aligned protagonist (%)")
    ax.set_title("Hyperparameter effect on demographic defaulting\n(implicit + semi-explicit prompts, all models)")
    ax.legend(frameon=True, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%g%%"))
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/fig6_hyperparameter_effect.png")
    plt.close(fig)
    print("Saved fig6_hyperparameter_effect.png")


if __name__ == "__main__":
    fig1_joint_effect()
    fig2_joint_effect_by_model()
    fig3_role_defaults()
    fig4_model_comparison()
    fig5_tiered_summary()
    fig6_hyperparameter_effect()
    print("\nAll figures saved to", OUTPUT_DIR)
