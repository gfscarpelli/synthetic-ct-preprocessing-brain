import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Imposta il font globale
plt.rcParams['font.family'] = 'Arial'

# ------------------------------------------------------------------
# Parametri
# ------------------------------------------------------------------
excel_file = "MAE_BIAS_patient.xlsx"   # file con tutti i pazienti
bin_width_mae = 10
bin_width_bias = 10
use_abs_bias = False   # False = tieni il bias con segno

# ------------------------------------------------------------------
# Caricamento e concatenazione di tutti i fogli (un foglio = un paziente)
# ------------------------------------------------------------------
sheets = pd.read_excel(excel_file, sheet_name=None)

all_rows = []
for paz_name, df in sheets.items():
    mae_cols = [c for c in df.columns if "MAE" in str(c).upper()]
    bias_cols = [c for c in df.columns if "BIAS" in str(c).upper()]
    if not mae_cols or not bias_cols:
        continue

    mae_col = mae_cols[0]
    bias_col = bias_cols[0]

    tmp = df[[mae_col, bias_col]].copy()
    tmp.columns = ["MAE", "BIAS"]
    tmp["Paziente"] = paz_name
    all_rows.append(tmp)

if not all_rows:
    raise RuntimeError("Nessun dato MAE/BIAS trovato nei fogli dell'Excel.")

data = pd.concat(all_rows, ignore_index=True)

# ------------------------------------------------------------------
# Funzioni di utilità per binning e conteggi
# ------------------------------------------------------------------
def make_bins(values, width):
    v = values[~np.isnan(values)]
    vmin, vmax = np.min(v), np.max(v)
    left = np.floor(vmin / width) * width
    right = np.ceil(vmax / width) * width
    edges = np.arange(left, right + width, width)
    return edges

def stats_in_bins(values, width):
    """
    Restituisce DataFrame con:
    - range: etichetta intervallo
    - n: conteggio
    - mean: media nel bin
    - std: deviazione standard nel bin (per i baffi)
    """
    edges = make_bins(values, width)
    binned = pd.cut(values, bins=edges, right=False, include_lowest=True)

    grouped = pd.DataFrame({"val": values, "bin": binned}).groupby("bin")
    counts = grouped["val"].count()
    means = grouped["val"].mean()
    stds = grouped["val"].std()

    ranges = []
    for iv in counts.index:
        l, r = int(iv.left), int(iv.right)
        ranges.append(f"[{l},{r}]")

    out = pd.DataFrame({
        "range": ranges,
        "n": counts.values,
        "mean": means.values,
        "std": stds.values,
    })

    # Ordina dal range più alto al più basso
    out = out.iloc[::-1].reset_index(drop=True)
    return out

plt.rcParams.update({
    "font.size": 14,
    "axes.labelsize": 16,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
})

# ------------------------------------------------------------------
# MAE: conteggi + baffi
# ------------------------------------------------------------------
mae_vals = data["MAE"].values.astype(float)
mae_stats = stats_in_bins(mae_vals, bin_width_mae)

fig_mae, ax_mae = plt.subplots(figsize=(12, 6))

x = np.arange(len(mae_stats))
# niente contorno nero: edgecolor="none"
ax_mae.bar(x, mae_stats["n"], color="#8CA8B6", edgecolor="none")

# baffi (std del MAE nel bin), centrati sull'altezza della barra
ax_mae.errorbar(
    x,
    mae_stats["n"],
    yerr=mae_stats["std"],
    fmt="none",
    ecolor="black",
    elinewidth=1.2,
    capsize=4,
)

ax_mae.set_xticks(x)
ax_mae.set_xticklabels(mae_stats["range"])

ax_mae.set_xlabel("Intervalli di MAE [HU]")
ax_mae.set_ylabel("Numero di sCT")
ax_mae.set_title("Mean Absolute Error (MAE)")

# numerini un po' più distanziati dai baffi (+3 invece di +0.5)
for xi, n in zip(x, mae_stats["n"]):
    ax_mae.text(xi, n + 3, f"n={int(n)}", ha="center", va="bottom", fontsize=10)

ax_mae.grid(axis="y", linestyle="--", alpha=0.4)
fig_mae.tight_layout()
fig_mae.savefig("MAE_range_counts(1).png", dpi=300)
# plt.show()

# ------------------------------------------------------------------
# BIAS: conteggi + baffi
# ------------------------------------------------------------------
if use_abs_bias:
    bias_vals = np.abs(data["BIAS"].values.astype(float))
    bias_xlabel = "Intervalli di |Bias| [HU]"
else:
    bias_vals = data["BIAS"].values.astype(float)
    bias_xlabel = "Intervalli di Bias [HU]"

bias_stats = stats_in_bins(bias_vals, bin_width_bias)

fig_bias, ax_bias = plt.subplots(figsize=(12, 6))

x = np.arange(len(bias_stats))
ax_bias.bar(x, bias_stats["n"], color="#ED9F65", edgecolor="none")

ax_bias.errorbar(
    x,
    bias_stats["n"],
    yerr=bias_stats["std"],
    fmt="none",
    ecolor="black",
    elinewidth=1.2,
    capsize=4,
)

ax_bias.set_xticks(x)
ax_bias.set_xticklabels(bias_stats["range"])

ax_bias.set_xlabel(bias_xlabel)
ax_bias.set_ylabel("Numero di sCT")
ax_bias.set_title("Bias")

for xi, n in zip(x, bias_stats["n"]):
    ax_bias.text(xi, n + 3.8, f"n={int(n)}", ha="center", va="bottom", fontsize=10)

ax_bias.grid(axis="y", linestyle="--", alpha=0.4)
fig_bias.tight_layout()
fig_bias.savefig("BIAS_range_counts(2).png", dpi=300)
plt.show()
