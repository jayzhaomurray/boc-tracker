"""
Bank of Canada Tracker — data fetcher and dashboard builder.

Run:    python fetch_data.py
Output: index.html  (open in any browser)
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timezone


# ── Series identifiers ────────────────────────────────────────────────────────
#
# Statistics Canada WDS vector IDs.
# To look up or verify a vector, visit:
#   https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector/{ID}
#
# Expected value ranges are noted — use these to sanity-check the output.

CPI_VECTOR   = 41690914  # Table 18-10-0006-01: All-items CPI, Canada, not seasonally adj.
                         # Expected range: ~160–175 (index, 2002=100)

UNEMP_VECTOR = 2062815   # Table 14-10-0287-01: Unemployment rate, Canada, seasonally adj.
                         # Expected range: ~5–10 (percent)
                         # If values are in the 1,000s, this is the unemployment COUNT not
                         # the RATE — update the vector ID (see table browser link above).

# Bank of Canada Valet API series key.
# Browse all series: https://www.bankofcanada.ca/valet/lists/series/json
# API docs:          https://www.bankofcanada.ca/valet/docs

YIELD_2YR_KEY = "BD.CDN.2YR.DQ.YLD"  # 2-yr GoC benchmark bond yield, daily
                                       # Expected range: ~1–5 (percent)


# ── Data fetchers ─────────────────────────────────────────────────────────────

def fetch_statscan(vector_id: int, n_periods: int = 120) -> pd.DataFrame:
    """Fetch the last n_periods observations for a Statistics Canada WDS vector."""
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    r = requests.post(
        url,
        json=[{"vectorId": vector_id, "latestN": n_periods}],
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()

    # The API returns a list matching the input list; we always send one vector.
    item = payload[0]
    if item.get("status") != "SUCCESS":
        raise ValueError(
            f"StatsCan API returned an error for vector {vector_id}:\n{item}"
        )

    points = item["object"]["vectorDataPoint"]
    df = pd.DataFrame(points)[["refPer", "value"]].copy()
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna().sort_values("date").reset_index(drop=True)


def fetch_boc_valet(series_key: str, start_date: str) -> pd.DataFrame:
    """Fetch observations from the Bank of Canada Valet API."""
    url = f"https://www.bankofcanada.ca/valet/observations/{series_key}/json"
    r = requests.get(url, params={"start_date": start_date}, timeout=30)
    r.raise_for_status()
    payload = r.json()

    if "observations" not in payload:
        raise ValueError(
            f"BoC Valet returned no observations for series '{series_key}'.\n"
            f"Check the series key at: https://www.bankofcanada.ca/valet/lists/series/json\n"
            f"Response: {payload}"
        )

    records = [
        {"date": ob["d"], "value": float(ob[series_key]["v"])}
        for ob in payload["observations"]
        if ob.get(series_key, {}).get("v") is not None
    ]
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


# ── Chart builder ─────────────────────────────────────────────────────────────

def build_figure(cpi: pd.DataFrame, unemp: pd.DataFrame, yield_2yr: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=[
            "Consumer Price Index — All Items, Canada (2002=100)",
            "Unemployment Rate — Canada, Seasonally Adjusted (%)",
            "2-Year Government of Canada Benchmark Bond Yield (%)",
        ],
        vertical_spacing=0.10,
    )

    fig.add_trace(go.Scatter(
        x=cpi["date"], y=cpi["value"],
        name="CPI",
        line=dict(color="#1f6aa5", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=unemp["date"], y=unemp["value"],
        name="Unemployment Rate",
        line=dict(color="#c0392b", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra></extra>",
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=yield_2yr["date"], y=yield_2yr["value"],
        name="2yr Yield",
        line=dict(color="#27ae60", width=1.5),
        hovertemplate="%{x|%b %d, %Y}<br>%{y:.2f}%<extra></extra>",
    ), row=3, col=1)

    fig.update_layout(
        height=840,
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        margin=dict(l=16, r=16, t=48, b=16),
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False)

    return fig


# ── HTML page assembly ────────────────────────────────────────────────────────

_CSS = """\
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 980px;
    margin: 0 auto;
    padding: 36px 20px 64px;
    background: #ffffff;
    color: #1a1a1a;
  }
  .site-header { margin-bottom: 28px; }
  .site-header h1 { font-size: 1.45rem; font-weight: 700; margin: 0 0 6px; }
  .site-header .tagline { font-size: 0.88rem; color: #666; margin: 0 0 4px; }
  .site-header .updated { font-size: 0.78rem; color: #bbb; margin: 0; }
  .about {
    margin-top: 40px;
    padding: 13px 17px;
    background: #f7f7f7;
    border-left: 3px solid #ddd;
    font-size: 0.8rem;
    color: #666;
    line-height: 1.7;
  }
  .about a { color: #1a5276; text-decoration: none; }
  .about a:hover { text-decoration: underline; }
"""

# Update this to your real name if you'd like it on the page.
AUTHOR_DISPLAY_NAME = "jayzhaomurray"


def inject_html(raw_html: str, last_updated: str) -> str:
    """Post-process Plotly's HTML output to add a header, footer, and CSS."""
    header = (
        '<div class="site-header">\n'
        '  <h1>Bank of Canada Tracker</h1>\n'
        '  <p class="tagline">Tracking the indicators behind Bank of Canada policy decisions</p>\n'
        '  <p class="updated">Last updated: ' + last_updated + '</p>\n'
        '</div>\n'
    )
    about = (
        '<div class="about">\n'
        '  <strong>About this dashboard</strong> &mdash;\n'
        '  Built by <a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '">'
        + AUTHOR_DISPLAY_NAME + '</a> using public data from\n'
        '  <a href="https://www150.statcan.gc.ca">Statistics Canada</a> and the\n'
        '  <a href="https://www.bankofcanada.ca/valet/docs">Bank of Canada Valet API</a>.\n'
        '  Updated daily via GitHub Actions.\n'
        '  <a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '/boc-tracker">'
        'View source on GitHub</a>.\n'
        '</div>\n'
    )
    raw_html = raw_html.replace("</head>", "<style>\n" + _CSS + "</style>\n</head>", 1)
    raw_html = raw_html.replace("<body>", "<body>\n" + header, 1)
    raw_html = raw_html.replace("</body>", about + "</body>", 1)
    return raw_html


# ── Main ──────────────────────────────────────────────────────────────────────

def build():
    print("Fetching CPI from Statistics Canada...")
    cpi = fetch_statscan(CPI_VECTOR, n_periods=120)
    print(f"  -> {len(cpi)} months; latest: {cpi['date'].max().strftime('%Y-%m')} = {cpi['value'].iloc[-1]:.1f}")

    print("Fetching unemployment rate from Statistics Canada...")
    unemp = fetch_statscan(UNEMP_VECTOR, n_periods=120)
    print(f"  -> {len(unemp)} months; latest: {unemp['date'].max().strftime('%Y-%m')} = {unemp['value'].iloc[-1]:.2f}")

    print("Fetching 2-year yield from Bank of Canada Valet API...")
    yield_2yr = fetch_boc_valet(YIELD_2YR_KEY, start_date="2018-01-01")
    print(f"  -> {len(yield_2yr)} days; latest: {yield_2yr['date'].max().strftime('%Y-%m-%d')} = {yield_2yr['value'].iloc[-1]:.2f}")

    fig = build_figure(cpi, unemp, yield_2yr)
    fig.write_html("index.html", include_plotlyjs="cdn", full_html=True)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    last_updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = inject_html(html, last_updated)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\nDone. Open index.html in your browser to view the dashboard.")


if __name__ == "__main__":
    build()
