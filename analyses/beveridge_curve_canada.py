"""
Canadian Beveridge curve — vacancy rate (Y) vs unemployment rate (X), monthly,
with 3M moving averages to denoise the NSA seasonality on the vacancy side.

Reads from data/ at project root. Outputs analyses/beveridge_curve_canada.html.

The post-2022 outward shift of the curve is the visually obvious feature —
that's the structural shift the Labour framework's Beveridge-curve caveat
references (matching efficiency / labour-force composition shifts post-COVID
immigration surge).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUT_PATH = Path(__file__).resolve().parent / "beveridge_curve_canada.html"


def load(name: str) -> pd.Series:
    df = pd.read_csv(DATA_DIR / f"{name}.csv", parse_dates=["date"])
    return df.set_index("date")["value"].sort_index()


def main() -> None:
    u = load("unemployment_rate")          # monthly SA, %
    v = load("job_vacancy_rate")           # monthly NSA, % (Table 14-10-0371; data starts 2015)

    # Inner-join on dates.
    df = pd.DataFrame({"u": u, "v": v}).dropna()

    # 3M MA on both. Vacancy is NSA so denoising matters most there; unemployment
    # is already SA but we smooth the same window for consistency.
    df["u_3m"] = df["u"].rolling(3, min_periods=2).mean()
    df["v_3m"] = df["v"].rolling(3, min_periods=2).mean()
    df = df.dropna()

    # Period buckets for colouring. Each bucket is a contiguous regime.
    def period(d: pd.Timestamp) -> str:
        if d < pd.Timestamp("2020-03-01"):
            return "Pre-pandemic (2015–Feb 2020)"
        if d < pd.Timestamp("2021-04-01"):
            return "COVID shock (Mar 2020–Mar 2021)"
        if d < pd.Timestamp("2023-01-01"):
            return "Post-COVID overheat (Apr 2021–Dec 2022)"
        if d < pd.Timestamp("2024-07-01"):
            return "Cooling (Jan 2023–Jun 2024)"
        return "Recent slack (Jul 2024–latest)"

    df["period"] = df.index.map(period)

    period_order = [
        "Pre-pandemic (2015–Feb 2020)",
        "COVID shock (Mar 2020–Mar 2021)",
        "Post-COVID overheat (Apr 2021–Dec 2022)",
        "Cooling (Jan 2023–Jun 2024)",
        "Recent slack (Jul 2024–latest)",
    ]
    period_colors = {
        "Pre-pandemic (2015–Feb 2020)":           "#1565c0",  # blue
        "COVID shock (Mar 2020–Mar 2021)":        "#7b1fa2",  # purple
        "Post-COVID overheat (Apr 2021–Dec 2022)":"#c62828",  # red
        "Cooling (Jan 2023–Jun 2024)":            "#ef6c00",  # orange
        "Recent slack (Jul 2024–latest)":         "#00897b",  # teal
    }

    fig = go.Figure()

    # Background grey line connecting all points in chronological order — shows the
    # full trajectory. Coloured markers on top are the period buckets.
    fig.add_trace(go.Scatter(
        x=df["u_3m"], y=df["v_3m"],
        mode="lines",
        line=dict(color="rgba(150,150,150,0.45)", width=1.5),
        showlegend=False,
        hoverinfo="skip",
    ))

    for p in period_order:
        sub = df[df["period"] == p]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["u_3m"], y=sub["v_3m"],
            mode="markers",
            name=p,
            marker=dict(size=7, color=period_colors[p], line=dict(width=0.5, color="white")),
            text=[d.strftime("%b %Y") for d in sub.index],
            hovertemplate="%{text}<br>U = %{x:.2f}%<br>V = %{y:.2f}%<extra>" + p + "</extra>",
        ))

    # Annotate the most recent point so it's findable.
    last = df.iloc[-1]
    fig.add_trace(go.Scatter(
        x=[last["u_3m"]], y=[last["v_3m"]],
        mode="markers+text",
        marker=dict(size=12, color="black", symbol="star"),
        text=[f" Latest ({df.index[-1].strftime('%b %Y')})"],
        textposition="middle right",
        textfont=dict(size=11, color="black"),
        showlegend=False,
        hoverinfo="skip",
    ))

    # 45° reference line for V/U = 1 (the M-S efficiency point) — only meaningful
    # if vacancy rate equals unemployment rate, which on these axes is U = V.
    # Note this is V/U = 1 only because both denominators are similar (LF for U,
    # employment+vacancies for V); structurally they're not identical, but the
    # diagonal still gives a visual reference for "vacancies as share of activity
    # similar to unemployment as share of LF."
    line_max = max(df["u_3m"].max(), df["v_3m"].max()) * 1.05
    fig.add_trace(go.Scatter(
        x=[0, line_max], y=[0, line_max],
        mode="lines",
        line=dict(color="rgba(100,100,100,0.4)", width=1, dash="dot"),
        name="V = U (rough V/U ≈ 1 reference)",
        hoverinfo="skip",
    ))

    fig.update_layout(
        title=dict(
            text="Canadian Beveridge curve (monthly, 3M MA)<br>"
                 "<sub>Vacancy rate (NSA, Table 14-10-0371) vs unemployment rate (SA, Table 14-10-0287); "
                 "data starts 2015. Post-COVID outward shift visible.</sub>",
            x=0.02, xanchor="left",
            font=dict(size=14),
        ),
        xaxis=dict(title="Unemployment rate (%, 3M MA)", showgrid=True, gridcolor="#ebebeb", zeroline=False),
        yaxis=dict(title="Vacancy rate (%, 3M MA)", showgrid=True, gridcolor="#ebebeb", zeroline=False),
        height=600, width=900,
        plot_bgcolor="#fafafa", paper_bgcolor="#ffffff",
        font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"),
        hovermode="closest",
        legend=dict(yanchor="top", y=0.98, xanchor="right", x=0.98, bgcolor="rgba(255,255,255,0.85)"),
        margin=dict(l=70, r=30, t=80, b=60),
    )

    fig.write_html(str(OUT_PATH), include_plotlyjs="cdn")
    print(f"Wrote: {OUT_PATH}")
    print(f"Periods plotted: {df['period'].value_counts().to_dict()}")
    print(f"Date range: {df.index[0].strftime('%b %Y')} to {df.index[-1].strftime('%b %Y')}")
    print(f"U range (3M MA): {df['u_3m'].min():.2f}% to {df['u_3m'].max():.2f}%")
    print(f"V range (3M MA): {df['v_3m'].min():.2f}% to {df['v_3m'].max():.2f}%")


if __name__ == "__main__":
    main()
