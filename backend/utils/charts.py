"""
Chart generation utilities using matplotlib.

All charts are rendered server-side with the non-interactive 'Agg' backend
(required since Flask/Celery run without a display) and returned as
base64-encoded PNG strings, ready to embed directly in <img> tags or emails
via a `data:image/png;base64,...` URI.
"""

import base64
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

# Palette matched to the frontend's navy/blue design system.
NAVY = "#00264d"
BLUE = "#00498d"
BLUE_LIGHT = "#5295d3"
GREEN = "#3b6d11"
AMBER = "#854f0b"
RED = "#a32d2d"
GRAY = "#8a8f98"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#d9dce1",
        "axes.labelcolor": "#3a3f4b",
        "text.color": "#3a3f4b",
        "xtick.color": "#6c7280",
        "ytick.color": "#6c7280",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def _fig_to_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight", transparent=False)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("ascii")


def _empty_chart(message="No data available yet"):
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=11, color=GRAY)
    ax.axis("off")
    return _fig_to_base64(fig)


def applications_by_status_chart(counts):
    """counts: dict like {'Applied': 10, 'Shortlisted': 4, ...}"""
    labels = [label for label, value in counts.items() if value]
    values = [value for value in counts.values() if value]
    if not values:
        return _empty_chart("No applications yet")

    color_map = {
        "Applied": BLUE_LIGHT,
        "Shortlisted": AMBER,
        "Selected": GREEN,
        "Rejected": RED,
    }
    colors = [color_map.get(label, GRAY) for label in labels]

    fig, ax = plt.subplots(figsize=(5, 3.6))
    wedges, _texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
        startangle=90,
        wedgeprops={"linewidth": 2, "edgecolor": "white"},
        textprops={"fontsize": 9},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    ax.set_title("Applications by Status", fontsize=12, fontweight="bold", color=NAVY, pad=12)
    ax.axis("equal")
    return _fig_to_base64(fig)


def drives_by_status_chart(counts):
    """counts: dict like {'Upcoming': 3, 'Ongoing': 2, 'Completed': 5, 'Pending': 1}"""
    labels = list(counts.keys())
    values = list(counts.values())
    if not any(values):
        return _empty_chart("No drives yet")

    color_map = {
        "Upcoming": BLUE_LIGHT,
        "Ongoing": AMBER,
        "Completed": GREEN,
        "Pending": GRAY,
    }
    colors = [color_map.get(label, BLUE) for label in labels]

    fig, ax = plt.subplots(figsize=(5, 3.6))
    bars = ax.bar(labels, values, color=colors, width=0.55)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, str(value),
                ha="center", va="bottom", fontsize=9, fontweight="bold", color=NAVY)
    ax.set_title("Placement Drives by Status", fontsize=12, fontweight="bold", color=NAVY, pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("Drives")
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    return _fig_to_base64(fig)


def monthly_trend_chart(month_labels, application_counts, selected_counts):
    """Line chart of applications vs selections over the last N months."""
    if not month_labels or not any(application_counts):
        return _empty_chart("Not enough data yet")

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(month_labels, application_counts, marker="o", color=BLUE, linewidth=2.2, label="Applications")
    ax.plot(month_labels, selected_counts, marker="o", color=GREEN, linewidth=2.2, label="Selections")
    ax.fill_between(month_labels, application_counts, color=BLUE, alpha=0.08)
    ax.set_title("Applications & Selections Trend", fontsize=12, fontweight="bold", color=NAVY, pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    ax.set_ylim(bottom=0)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    return _fig_to_base64(fig)


def top_companies_chart(companies):
    """companies: list of (name, application_count) tuples, highest first."""
    if not companies:
        return _empty_chart("No applications yet")

    names = [name for name, _ in companies][::-1]
    counts = [count for _, count in companies][::-1]

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    bars = ax.barh(names, counts, color=BLUE_LIGHT, height=0.55)
    for bar, value in zip(bars, counts):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, str(value),
                va="center", fontsize=9, fontweight="bold", color=NAVY)
    ax.set_title("Top Recruiting Companies", fontsize=12, fontweight="bold", color=NAVY, pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel("Applications received")
    fig.tight_layout()
    return _fig_to_base64(fig)


def department_distribution_chart(counts):
    """counts: dict like {'CSE': 12, 'ECE': 5, ...}"""
    if not counts:
        return _empty_chart("No department data yet")

    labels = list(counts.keys())
    values = list(counts.values())
    palette = [NAVY, BLUE, BLUE_LIGHT, GREEN, AMBER, RED, GRAY]
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(5, 3.6))
    ax.bar(labels, values, color=colors, width=0.55)
    ax.set_title("Applications by Department", fontsize=12, fontweight="bold", color=NAVY, pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("Applications")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    fig.tight_layout()
    return _fig_to_base64(fig)
