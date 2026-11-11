"""Shared matplotlib style (reference categorical palette, fixed order; recessive axes)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
TEXT, TEXT2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
COHORT_ORDER = ["dev_test", "ext_shdb-af", "ext_cpsc2021", "ext_icentia11k"]
COHORT_LABEL = {"dev_test": "Development test (USA)", "ext_shdb-af": "SHDB-AF (Japan)",
                "ext_cpsc2021": "CPSC2021 (China)", "ext_icentia11k": "Icentia11k (Canada)",
                "ext_pooled": "Pooled external", "calB": "Conformal calibration"}
COHORT_COLOR = {c: SERIES[i] for i, c in enumerate(COHORT_ORDER)}
DET_COLOR = {"Classical-LR": SERIES[0], "LightGBM": SERIES[1], "RRNet": SERIES[2]}


def apply():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
        "axes.edgecolor": TEXT2, "axes.labelcolor": TEXT, "xtick.color": TEXT2, "ytick.color": TEXT2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 7,
        "lines.linewidth": 2, "savefig.dpi": 300, "figure.dpi": 150, "savefig.bbox": "tight"})


def save(fig, path):
    fig.savefig(path + ".png", dpi=300)
    fig.savefig(path + ".tiff", dpi=300, pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
