/* eslint-disable */
// Inflation deep-dive page composition.

const { useState: useStateInf } = React;

function InflationPage() {
  const [theme, setTheme] = useStateInf("paper");
  const [coreActive, setCoreActive] = useStateInf(["trim", "median", "common"]);
  const toggleCore = (id) =>
    setCoreActive((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id]));

  return (
    <div data-theme={theme === "vault" ? "vault" : null} style={{ minHeight: "100vh", color: "var(--ink)" }} data-screen-label="Inflation deep-dive">
      <Masthead theme={theme} onToggleTheme={() => setTheme(theme === "vault" ? "paper" : "vault")} />

      <main style={{ maxWidth: 1240, margin: "0 auto", padding: "36px 32px 0" }}>
        {/* Breadcrumb + title */}
        <div style={{ marginBottom: 28 }}>
          <Eyebrow stamp="Statistics Canada · Released Apr 15, 2026" dot>
            <a href="index.html" style={{ color: "inherit", textDecoration: "none" }}>Splash</a>
            <span style={{ color: "var(--ink-quiet)", margin: "0 6px" }}>/</span>
            Inflation
          </Eyebrow>
          <FoilRule style={{ width: 56, margin: "10px 0 12px" }} />
          <h1 className="display-2" style={{ marginBottom: 10 }}>
            Headline is sticky 0.3pp above target; core measures have rebroadened.
          </h1>
          <p className="lede" style={{ maxWidth: "68ch", margin: 0 }}>
            Trim and median both ticked up in March. Services CPI is decelerating but slowly. Goods disinflation has stalled at +1.8% Y/Y, and breadth — the share of basket components above 3% Y/Y — sits at the 65th percentile of its 10-year range.
          </p>
        </div>

        {/* Mini-KPI strip */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 28 }}>
          <KPITile label="Headline CPI" stamp="Mar" value="2.3" unit="%" delta="↑ 0.1 pp m/m" tone="above" sub={{ pill: "Above 2%", text: "Trim 2.1 · Median 2.2." }} />
          <KPITile label="Trim" stamp="Mar" value="2.1" unit="%" delta="↑ 0.1 pp m/m" tone="above" sub={{ pill: "Above 2%", text: "Bank of Canada preferred." }} />
          <KPITile label="Median" stamp="Mar" value="2.2" unit="%" delta="↑ 0.1 pp m/m" tone="above" sub={{ pill: "Above 2%", text: "Bank of Canada preferred." }} />
          <KPITile label="Breadth >3%" stamp="Mar" value="34" unit="%" delta="↑ 1.4 pp m/m" tone="above" sub={{ pill: "Elevated", text: "Share of basket components." }} />
        </div>

        {/* Two-column chart row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
          <ChartCard
            eyebrow="Inflation · 02"
            stamp="Statistics Canada · CPI"
            title="CPI components — volatile decomposition"
            legend={
              <LegendChips
                items={[
                  { id: "headline", label: "Headline", color: "var(--cobalt)", kind: "line" },
                  { id: "food", label: "Food", color: "var(--cat-pine)", kind: "line" },
                  { id: "energy", label: "Energy", color: "var(--cat-amber)", kind: "line" },
                ]}
                active={["headline", "food", "energy"]}
              />
            }
            footnote="Food and energy are the loudest components; both have re-coupled with headline since late 2024."
          >
            <CPIComponentsChart width={566} height={260} visible={["headline", "food", "energy"]} />
          </ChartCard>

          <ChartCard
            eyebrow="Inflation · 03"
            stamp="Statistics Canada · CPI"
            title="Core measures — trim, median, common"
            legend={
              <LegendChips
                items={[
                  { id: "trim", label: "CPI-trim", color: "var(--cobalt)", kind: "line" },
                  { id: "median", label: "CPI-median", color: "var(--cat-plum)", kind: "line" },
                  { id: "common", label: "CPI-common", color: "var(--cat-teal)", kind: "line" },
                ]}
                active={coreActive}
                onToggle={toggleCore}
              />
            }
            footnote="All three are above the 2% target; trim and median have re-accelerated in the past quarter."
          >
            <CPIComponentsChart width={566} height={260} visible={["headline", "services", "goods"]} />
          </ChartCard>
        </div>

        {/* Sub-aggregate breadth table */}
        <div style={{ marginTop: 30, marginBottom: 12 }}>
          <Eyebrow stamp="Statistics Canada · CPI sub-aggregate basket weights">Breadth by sub-aggregate</Eyebrow>
          <FoilRule style={{ width: 56, margin: "8px 0 14px" }} />
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse", font: "500 13px/1.45 var(--font-sans)" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--rule)" }}>
              <th style={th()}>Sub-aggregate</th>
              <th style={th("right")}>Weight</th>
              <th style={th("right")}>Y/Y</th>
              <th style={th("right")}>3M AR</th>
              <th style={th("right")}>M/M</th>
              <th style={th("right")}>Contribution to headline</th>
              <th style={th("right")}>Status</th>
            </tr>
          </thead>
          <tbody>
            {[
              ["Food, purchased from stores", "11.0%", "+2.5", "+2.8", "+0.2", "+0.27 pp", "above"],
              ["Food, purchased from restaurants", "5.9%", "+3.4", "+3.1", "+0.3", "+0.20 pp", "above"],
              ["Shelter — owned accommodation", "16.2%", "+4.1", "+3.4", "+0.2", "+0.66 pp", "above"],
              ["Shelter — rented accommodation", "8.6%", "+5.8", "+5.2", "+0.4", "+0.50 pp", "above"],
              ["Household operations", "6.7%", "+1.6", "+1.2", "+0.1", "+0.11 pp", "on"],
              ["Clothing & footwear", "4.4%", "+0.9", "+0.4", "+0.0", "+0.04 pp", "on"],
              ["Transportation — purchased vehicles", "6.0%", "+0.4", "+1.1", "+0.0", "+0.02 pp", "on"],
              ["Transportation — gasoline", "4.0%", "+5.2", "+3.8", "−0.6", "+0.21 pp", "above"],
              ["Health & personal care", "5.2%", "+2.1", "+2.4", "+0.1", "+0.11 pp", "above"],
              ["Recreation, education & reading", "9.6%", "+1.3", "+0.9", "+0.0", "+0.12 pp", "on"],
            ].map((r, i) => (
              <tr key={i} style={{ borderBottom: "1px solid var(--rule)" }}>
                <td style={td()}>{r[0]}</td>
                <td style={td("right", true)}>{r[1]}</td>
                <td style={td("right", true)}>{r[2]}</td>
                <td style={td("right", true)}>{r[3]}</td>
                <td style={td("right", true)}>{r[4]}</td>
                <td style={td("right", true)}>{r[5]}</td>
                <td style={td("right")}><StatusPill tone={r[6]}>{r[6] === "above" ? "Above" : "On target"}</StatusPill></td>
              </tr>
            ))}
          </tbody>
        </table>

        <p className="caption" style={{ marginTop: 14, color: "var(--ink-quiet)" }}>
          Source: Statistics Canada Table 18-10-0004-01. Contribution computed from current-month basket weights × Y/Y change; rounding may cause aggregates not to sum.
        </p>
      </main>

      <Footer />
    </div>
  );
}

function th(align = "left") {
  return {
    textAlign: align,
    padding: "10px 14px 10px 0",
    font: "500 11px/1.4 var(--font-mono)",
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    color: "var(--ink-quiet)",
  };
}
function td(align = "left", num = false) {
  return {
    textAlign: align,
    padding: "10px 14px 10px 0",
    fontVariantNumeric: num ? "tabular-nums" : "normal",
    fontFamily: num ? "var(--font-mono)" : "var(--font-sans)",
    color: "var(--ink)",
  };
}

ReactDOM.createRoot(document.getElementById("root")).render(<InflationPage />);
window.requestAnimationFrame(() => { if (window.lucide) window.lucide.createIcons(); });
