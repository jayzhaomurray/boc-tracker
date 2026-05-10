/* eslint-disable */
// BoC Tracker UI Kit — Components
// All shared components for the dashboard recreation. Export to window at the end.

const FoilDot = ({ size = 10, style = {} }) => (
  <span
    aria-hidden
    style={{
      display: "inline-block",
      width: size,
      height: size,
      borderRadius: "50%",
      background: "var(--foil)",
      verticalAlign: "0.05em",
      ...style,
    }}
  />
);

const FoilRule = ({ thick = false, width = "100%", style = {} }) => (
  <div
    style={{
      height: thick ? 2 : 1,
      background: "var(--foil)",
      width,
      ...style,
    }}
  />
);

const Eyebrow = ({ children, stamp, dot = false, style = {} }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: 10,
      ...style,
    }}
  >
    <span className="eyebrow">{children}</span>
    {stamp && (
      <span
        className="mono"
        style={{ fontSize: 11, color: "var(--ink-quiet)" }}
      >
        · {stamp}
      </span>
    )}
    {dot && <FoilDot style={{ marginLeft: "auto" }} />}
  </div>
);

const StatusPill = ({ tone = "on", children }) => {
  const tones = {
    above: { c: "var(--vermillion)", bg: "var(--vermillion-tint)" },
    on: { c: "var(--cobalt)", bg: "var(--cobalt-tint)" },
    below: { c: "var(--cat-teal)", bg: "oklch(94% 0.03 195)" },
    tighten: { c: "var(--cat-amber)", bg: "oklch(94% 0.04 70)" },
    easing: { c: "var(--cat-pine)", bg: "oklch(94% 0.03 145)" },
  };
  const t = tones[tone];
  return (
    <span
      style={{
        font: "600 10px/1 var(--font-sans)",
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        padding: "4px 7px",
        borderRadius: "var(--r-pill)",
        border: `1px solid ${t.c}`,
        color: t.c,
        background: t.bg,
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        whiteSpace: "nowrap",
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: t.c,
        }}
      />
      {children}
    </span>
  );
};

const TierTag = ({ tier = 2 }) => {
  const tiers = {
    1: { bg: "oklch(94% 0.005 85)", c: "var(--ink-quiet)", b: "var(--rule)", l: "Tier 1 · Generated" },
    2: { bg: "var(--cobalt-tint)", c: "var(--cobalt)", b: "oklch(80% 0.06 260)", l: "Tier 2 · Auto-verified" },
    3: { bg: "oklch(94% 0.03 145)", c: "var(--cat-pine)", b: "oklch(78% 0.08 145)", l: "Tier 3 · User-verified" },
  };
  const t = tiers[tier];
  return (
    <span
      style={{
        font: "600 10px/1 var(--font-mono)",
        letterSpacing: "0.04em",
        padding: "4px 7px",
        borderRadius: "var(--r-xs)",
        background: t.bg,
        color: t.c,
        border: `1px solid ${t.b}`,
      }}
    >
      {t.l}
    </span>
  );
};

const KPITile = ({ label, stamp, value, unit, delta, deltaDir = "up", tone = "on", subtone, sub }) => (
  <div
    style={{
      background: "var(--card)",
      border: "1px solid var(--rule)",
      borderRadius: "var(--r-md)",
      padding: "14px 16px",
      boxShadow: "var(--shadow-card)",
      display: "flex",
      flexDirection: "column",
      gap: 0,
    }}
  >
    <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
      <span className="eyebrow">{label}</span>
      <span className="mono" style={{ fontSize: 10, color: "var(--ink-quiet)" }}>{stamp}</span>
    </div>
    <div
      className="data-xl"
      style={{ margin: "12px 0 6px", letterSpacing: "-0.01em" }}
    >
      {value}
      {unit && <span style={{ color: "var(--ink-quiet)", fontSize: "0.4em", marginLeft: 4, letterSpacing: 0 }}>{unit}</span>}
    </div>
    {delta && (
      <div
        className="mono"
        style={{
          fontSize: 11,
          color: deltaDir === "down" ? "var(--cat-pine)" : "var(--vermillion)",
        }}
      >
        {delta}
      </div>
    )}
    {sub && (
      <div
        className="small"
        style={{
          marginTop: 10,
          paddingTop: 10,
          borderTop: "1px solid var(--rule)",
          color: "var(--ink-sub)",
          display: "flex",
          alignItems: "center",
          gap: 8,
          flexWrap: "wrap",
        }}
      >
        <StatusPill tone={subtone || tone}>{sub.pill}</StatusPill>
        {sub.text && <span>{sub.text}</span>}
      </div>
    )}
  </div>
);

const ToolbarPills = ({ options, value, onChange }) => (
  <div
    style={{
      display: "inline-flex",
      border: "1px solid var(--rule-strong)",
      borderRadius: "var(--r-sm)",
      overflow: "hidden",
      background: "var(--card)",
    }}
  >
    {options.map((o, i) => {
      const isActive = o === value;
      return (
        <button
          key={o}
          onClick={() => onChange && onChange(o)}
          style={{
            font: "500 12px/1 var(--font-mono)",
            padding: "7px 12px",
            color: isActive ? "var(--cobalt)" : "var(--ink-sub)",
            background: isActive ? "var(--cobalt-tint)" : "transparent",
            cursor: "pointer",
            border: 0,
            borderRight: i < options.length - 1 ? "1px solid var(--rule)" : 0,
            position: "relative",
          }}
        >
          {o}
          {isActive && (
            <span
              style={{
                position: "absolute",
                left: 8,
                right: 8,
                bottom: 0,
                height: 2,
                background: "var(--foil)",
              }}
            />
          )}
        </button>
      );
    })}
  </div>
);

const ChartCard = ({ eyebrow, stamp, title, toolbar, footnote, children, legend }) => (
  <section
    style={{
      background: "var(--card)",
      border: "1px solid var(--rule)",
      borderRadius: "var(--r-lg)",
      boxShadow: "var(--shadow-card)",
      padding: "16px 18px 14px",
      display: "flex",
      flexDirection: "column",
      gap: 10,
    }}
  >
    <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
      <div>
        <Eyebrow stamp={stamp}>{eyebrow}</Eyebrow>
        <h3 style={{ margin: "4px 0 0", font: "600 19px/1.25 var(--font-display)", letterSpacing: "-0.02em" }}>
          {title}
        </h3>
      </div>
      {toolbar}
    </div>
    <div>{children}</div>
    {legend && <div style={{ borderTop: "1px solid var(--rule)", paddingTop: 10 }}>{legend}</div>}
    {footnote && (
      <div className="footnote" style={{ paddingTop: legend ? 6 : 8, borderTop: legend ? 0 : "1px solid var(--rule)" }}>
        {footnote}
      </div>
    )}
  </section>
);

const LegendChips = ({ items, active = [], onToggle }) => (
  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px 12px" }}>
    {items.map((it) => {
      const isOff = !active.includes(it.id);
      return (
        <span
          key={it.id}
          onClick={() => onToggle && onToggle(it.id)}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            font: "500 12px/1 var(--font-sans)",
            color: isOff ? "var(--ink-faint)" : "var(--ink-sub)",
            padding: "6px 8px",
            borderRadius: "var(--r-sm)",
            cursor: "pointer",
            opacity: isOff ? 0.55 : 1,
            userSelect: "none",
          }}
        >
          {it.kind === "band" ? (
            <span
              style={{
                width: 14,
                height: 12,
                borderRadius: 2,
                background: "var(--band-fill)",
                border: "1px solid var(--rule-strong)",
              }}
            />
          ) : (
            <span
              style={{
                width: 12,
                height: it.kind === "line" ? 2 : 10,
                borderRadius: 2,
                background: it.color,
                borderTop: it.dash ? `2px dashed ${it.color}` : 0,
                ...(it.dash ? { background: "transparent" } : {}),
              }}
            />
          )}
          {it.label}
        </span>
      );
    })}
  </div>
);

const Masthead = ({ theme, onToggleTheme }) => (
  <header
    style={{
      position: "sticky",
      top: 0,
      zIndex: 10,
      backdropFilter: "blur(8px)",
      WebkitBackdropFilter: "blur(8px)",
      background: "color-mix(in oklch, var(--paper) 90%, transparent)",
      borderBottom: "1px solid var(--rule)",
    }}
  >
    <div
      style={{
        maxWidth: 1240,
        margin: "0 auto",
        padding: "12px 32px 10px",
        display: "flex",
        alignItems: "center",
        gap: 24,
      }}
    >
      <a href="#" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none", color: "var(--ink)" }}>
        <img src="../../assets/monogram.svg" alt="" width="22" height="22" />
        <span style={{ font: "600 18px/1 var(--font-display)", letterSpacing: "-0.02em" }}>
          BoC Tracker
        </span>
      </a>
      <nav style={{ display: "flex", gap: 18, marginLeft: 32 }}>
        {["Overview", "Monetary", "Inflation", "GDP", "Labour", "Housing", "Financial", "Trade"].map((n, i) => (
          <a
            key={n}
            href="#"
            className="link-foil"
            style={{
              font: "500 12px/1 var(--font-sans)",
              color: i === 0 ? "var(--ink)" : "var(--ink-sub)",
              textTransform: "none",
            }}
          >
            {n}
          </a>
        ))}
      </nav>
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 14 }}>
        <span
          className="mono"
          style={{
            fontSize: 11,
            color: "var(--ink-quiet)",
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <FoilDot size={8} /> refreshed&nbsp;Apr&nbsp;30 · 04:12&nbsp;ET
        </span>
        <button
          onClick={onToggleTheme}
          aria-label="Toggle theme"
          style={{
            font: "500 11px/1 var(--font-mono)",
            padding: "6px 10px",
            border: "1px solid var(--rule-strong)",
            background: "var(--card)",
            color: "var(--ink-sub)",
            borderRadius: "var(--r-sm)",
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <i data-lucide={theme === "vault" ? "sun" : "moon"} style={{ width: 13, height: 13 }} />
          {theme === "vault" ? "Paper" : "Vault"}
        </button>
      </div>
    </div>
    <FoilRule />
  </header>
);

const Footer = () => (
  <footer style={{ borderTop: "1px solid var(--rule)", padding: "24px 32px 40px", marginTop: 64, color: "var(--ink-quiet)" }}>
    <div style={{ maxWidth: 1240, margin: "0 auto", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
      <div className="small">
        BoC Tracker · a personal data dashboard · built nightly via GitHub Actions
      </div>
      <div className="small">
        <a className="link-quiet" href="#">Source</a> ·{" "}
        <a className="link-quiet" href="#">CSVs</a> ·{" "}
        <a className="link-quiet" href="#">Analysis framework</a>
      </div>
    </div>
  </footer>
);

Object.assign(window, {
  FoilDot,
  FoilRule,
  Eyebrow,
  StatusPill,
  TierTag,
  KPITile,
  ToolbarPills,
  ChartCard,
  LegendChips,
  Masthead,
  Footer,
});
