/* eslint-disable */
// Splash page composition for the BoC Tracker UI kit.

const { useState } = React;

function SplashPage() {
  const [theme, setTheme] = useState("paper");
  const [policyTransform, setPolicyTransform] = useState("Level");
  const [policyRange, setPolicyRange] = useState("10Y");
  const [cpiTransform, setCpiTransform] = useState("Y/Y");
  const [cpiRange, setCpiRange] = useState("10Y");
  const [cpiActive, setCpiActive] = useState(["headline", "food", "energy"]);

  const toggleCpi = (id) =>
    setCpiActive((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );

  const cpiItems = [
    { id: "headline", label: "Headline", color: "var(--cobalt)", kind: "line" },
    { id: "food", label: "Food", color: "var(--cat-pine)", kind: "line" },
    { id: "energy", label: "Energy", color: "var(--cat-amber)", kind: "line" },
    { id: "goods", label: "Goods", color: "var(--cat-teal)", kind: "line" },
    { id: "services", label: "Services", color: "var(--cat-plum)", kind: "line" },
  ];

  return (
    <div data-theme={theme === "vault" ? "vault" : null} style={{ minHeight: "100vh", color: "var(--ink)" }} data-screen-label="Splash">
      <Masthead theme={theme} onToggleTheme={() => setTheme(theme === "vault" ? "paper" : "vault")} />

      <main style={{ maxWidth: 1240, margin: "0 auto", padding: "36px 32px 0" }}>
        {/* Title block */}
        <div style={{ marginBottom: 28 }}>
          <Eyebrow stamp="Refreshed Apr 30, 2026 · 04:12 ET" dot>Where Canada stands</Eyebrow>
          <FoilRule style={{ width: 56, margin: "10px 0 12px" }} />
          <h1 className="display-2" style={{ marginBottom: 10 }}>
            The Bank is on hold at the upper edge of neutral.
          </h1>
          <p className="lede" style={{ maxWidth: "68ch", margin: 0 }}>
            Three consecutive meetings without action. Headline CPI sits 0.3pp above target with breadth still elevated; the labour market is loose but not breaking; the 2Y GoC prices one cut over the next twelve months.
          </p>
          <div style={{ marginTop: 14, display: "flex", gap: 8, flexWrap: "wrap" }}>
            <TierTag tier={3} />
            <TierTag tier={2} />
          </div>
        </div>

        {/* 5 KPI tiles */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12, marginBottom: 28 }}>
          <KPITile
            label="Monetary policy"
            stamp="Apr 30"
            value="2.75"
            unit="%"
            delta="0 bp · 3 mtgs flat"
            deltaDir="down"
            tone="on"
            sub={{ pill: "In band", text: "Upper edge of 2.25–3.25%." }}
          />
          <KPITile
            label="Headline CPI"
            stamp="Mar"
            value="2.3"
            unit="%"
            delta="↑ 0.1 pp m/m"
            tone="above"
            sub={{ pill: "Above 2%", text: "Trim 2.1 · Median 2.2." }}
          />
          <KPITile
            label="Real GDP Q/Q AR"
            stamp="Q4"
            value="1.8"
            unit="%"
            delta="↓ 0.4 pp q/q"
            deltaDir="down"
            tone="on"
            subtone="on"
            sub={{ pill: "Near potential", text: "Output gap −0.3%." }}
          />
          <KPITile
            label="Unemployment"
            stamp="Apr"
            value="6.4"
            unit="%"
            delta="↓ 0.1 pp m/m"
            deltaDir="down"
            tone="on"
            subtone="on"
            sub={{ pill: "Slack", text: "78th pct of 24m range." }}
          />
          <KPITile
            label="USDCAD"
            stamp="Apr 30"
            value="1.362"
            delta="↓ 0.021 m/m"
            deltaDir="down"
            tone="on"
            subtone="on"
            sub={{ pill: "Stable", text: "Below 1.45 stress corridor." }}
          />
        </div>

        {/* Hero chart: policy rate */}
        <div style={{ marginBottom: 20 }}>
          <ChartCard
            eyebrow="Monetary policy · 01"
            stamp="V39079 (BoC) · FEDFUNDS (FRED)"
            title="Policy rates vs neutral band — BoC and the Fed, 10Y"
            toolbar={
              <div style={{ display: "flex", gap: 10 }}>
                <ToolbarPills options={["Level", "M/M", "Δ12m"]} value={policyTransform} onChange={setPolicyTransform} />
                <ToolbarPills options={["2Y", "5Y", "10Y", "Max"]} value={policyRange} onChange={setPolicyRange} />
              </div>
            }
            legend={
              <LegendChips
                items={[
                  { id: "boc", label: "BoC overnight", color: "var(--cobalt)", kind: "line" },
                  { id: "fed", label: "Fed funds (upper, editorial)", color: "var(--vermillion)", kind: "line", dash: true },
                  { id: "band", label: "Neutral band (2.25–3.25%)", color: "var(--band-fill)", kind: "band" },
                ]}
                active={["boc", "fed", "band"]}
              />
            }
            footnote="BoC rate is a step series (discrete decisions); Fed is shown on the upper bound of the target range. Neutral band per Bank of Canada annual r* update."
          >
            <PolicyRateChart width={1166} height={320} />
          </ChartCard>
        </div>

        {/* CPI components chart */}
        <div style={{ marginBottom: 20 }}>
          <ChartCard
            eyebrow="Inflation · 02"
            stamp="Statistics Canada · CPI"
            title="CPI components — headline, food, energy, goods, services"
            toolbar={
              <div style={{ display: "flex", gap: 10 }}>
                <ToolbarPills options={["M/M", "3M AR", "Y/Y"]} value={cpiTransform} onChange={setCpiTransform} />
                <ToolbarPills options={["2Y", "5Y", "10Y", "Max"]} value={cpiRange} onChange={setCpiRange} />
              </div>
            }
            legend={<LegendChips items={cpiItems} active={cpiActive} onToggle={toggleCpi} />}
            footnote="The 2% target reference is the dotted line. Per the chart style guide, this chart leads with the volatile decomposition (headline + food + energy) so it tells a distinct story from the Core Inflation chart on the same page."
          >
            <CPIComponentsChart width={1166} height={280} visible={cpiActive} />
          </ChartCard>
        </div>

        {/* Deep-dive index */}
        <div style={{ marginTop: 36, marginBottom: 12 }}>
          <Eyebrow>Deep-dive pages</Eyebrow>
          <FoilRule style={{ width: 56, margin: "8px 0 0" }} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 0, borderTop: "1px solid var(--rule)", marginTop: 14 }}>
          {[
            { n: "03", title: "Inflation", lede: "Headline, core measures, breadth, sub-aggregates and inflation expectations." },
            { n: "04", title: "GDP & activity", lede: "Monthly real GDP, Q/Q AR, demand-side contribution decomposition." },
            { n: "05", title: "Labour", lede: "Unemployment trajectory, four wage measures, pass-through to services CPI." },
            { n: "06", title: "Housing", lede: "Starts, NHPI, permits as a leading indicator; CMHC supply gap." },
            { n: "07", title: "Financial conditions", lede: "WTI / Brent / WCS oil, USDCAD with stress corridor, BoC FX pass-through." },
            { n: "08", title: "Trade", lede: "Export composition; petrocurrency relationship; pass-through magnitudes." },
          ].map((d, i) => (
            <a
              key={d.n}
              href={d.title === "Inflation" ? "inflation.html" : "#"}
              className="link-quiet"
              style={{
                padding: "20px 18px 22px",
                borderBottom: "1px solid var(--rule)",
                borderRight: (i % 3 !== 2) ? "1px solid var(--rule)" : 0,
                display: "block",
                textDecoration: "none",
              }}
            >
              <div className="mono" style={{ fontSize: 11, color: "var(--ink-quiet)", marginBottom: 6 }}>{d.n}</div>
              <h3 style={{ font: "600 22px/1.15 var(--font-display)", letterSpacing: "-0.02em", margin: "0 0 6px" }}>{d.title}</h3>
              <p className="small" style={{ margin: 0, color: "var(--ink-sub)" }}>{d.lede}</p>
            </a>
          ))}
        </div>
      </main>

      <Footer />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<SplashPage />);

// Lucide icons for masthead
window.requestAnimationFrame(() => {
  if (window.lucide) window.lucide.createIcons();
});
