"""Génère les PNG de score pour les slides (fond crème, pas de cadre blanc).

matplotlib n'est pas une dépendance du package : script local, à lancer
quand on retouche les seuils. Sortie : pictures/presentations/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from sites_parapente.overlay import (
    ASPECT_FLOOR,
    PREFERRED_ASPECT_DEG,
    WEIGHT_ASPECT,
    WEIGHT_LANDCOVER,
    WEIGHT_SLOPE,
    aspect_score,
    slope_score,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pictures" / "presentations"

BG = "#f3eee6"
INK = "#1c1610"
ACCENT = "#8a6a12"
MUTED = "#5c564c"


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(BG)
    ax.figure.set_facecolor(BG)
    ax.tick_params(colors=MUTED)
    for spine in ax.spines.values():
        spine.set_color("#d4cdc2")
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def plot_slope(path: Path, xlabel: str) -> None:
    x = np.linspace(0, 55, 400)
    y = slope_score(x)
    fig, ax = plt.subplots(figsize=(10.2, 4.4), dpi=140)
    _style(ax)
    ax.plot(x, y, color=ACCENT, lw=2.8)
    ax.fill_between(x, y, color=ACCENT, alpha=0.12)
    ax.axvspan(16, 28, color=ACCENT, alpha=0.08)
    ax.set_xlim(0, 55)
    ax.set_ylim(-0.05, 1.12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Score")
    ax.set_xticks([0, 10, 16, 28, 42, 55])
    fig.tight_layout()
    fig.savefig(path, facecolor=BG, edgecolor="none")
    plt.close(fig)


def plot_aspect(path: Path, xlabel: str) -> None:
    x = np.linspace(0, 360, 361)
    y = aspect_score(x)
    fig, ax = plt.subplots(figsize=(10.2, 4.4), dpi=140)
    _style(ax)
    ax.plot(x, y, color=ACCENT, lw=2.8)
    ax.fill_between(x, y, color=ACCENT, alpha=0.12)
    ax.axhline(ASPECT_FLOOR, color=MUTED, ls="--", lw=1)
    ax.axvline(PREFERRED_ASPECT_DEG, color=ACCENT, ls=":", lw=1.2)
    ax.set_xlim(0, 360)
    ax.set_ylim(0, 1.12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Score")
    ax.set_xticks([0, 90, 180, 225, 270, 360])
    ax.set_xticklabels(["N", "E", "S", "SW", "W", "N"])
    fig.tight_layout()
    fig.savefig(path, facecolor=BG, edgecolor="none")
    plt.close(fig)


def plot_weights(path: Path, labels: list[str], xlabel: str) -> None:
    values = [WEIGHT_SLOPE, WEIGHT_ASPECT, WEIGHT_LANDCOVER]
    fig, ax = plt.subplots(figsize=(9.2, 4.2), dpi=140)
    _style(ax)
    bars = ax.barh(labels[::-1], values[::-1], color=ACCENT, height=0.55)
    ax.set_xlim(0, 0.7)
    ax.set_xlabel(xlabel)
    ax.bar_label(
        bars, labels=["50 %", "30 %", "20 %"][::-1], padding=8, color=INK
    )
    ax.tick_params(axis="y", labelsize=13)
    fig.tight_layout()
    fig.savefig(path, facecolor=BG, edgecolor="none")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    plot_slope(OUT / "score-pente.png", "Pente (°)")
    plot_slope(OUT / "score-pente-en.png", "Slope (°)")
    plot_aspect(OUT / "score-aspect.png", "Aspect (°), 0 = nord")
    plot_aspect(OUT / "score-aspect-en.png", "Aspect (°), 0 = north")
    plot_weights(
        OUT / "poids-overlay.png",
        ["Pente", "Aspect", "Sol ouvert"],
        "Poids",
    )
    plot_weights(
        OUT / "poids-overlay-en.png",
        ["Slope", "Aspect", "Open ground"],
        "Weight",
    )
    for name in (
        "score-pente.png",
        "score-pente-en.png",
        "score-aspect.png",
        "score-aspect-en.png",
        "poids-overlay.png",
        "poids-overlay-en.png",
    ):
        print(f"écrit {OUT / name}")
