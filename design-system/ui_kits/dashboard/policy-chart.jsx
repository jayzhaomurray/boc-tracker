/* eslint-disable */
// PolicyRateChart — the hero chart on the splash page.
// BoC overnight (step line) + Fed (step line, editorial overlay) + neutral band overlay.

function genStepSeries(meetings, w, h, ymin, ymax, padX = 36, padTop = 14, padBot = 26) {
  const minDate = meetings[0].t;
  const maxDate = meetings[meetings.length - 1].t;
  const xRange = maxDate - minDate;
  const innerW = w - padX - 12;
  const innerH = h - padTop - padBot;
  const xs = (t) => padX + ((t - minDate) / xRange) * innerW;
  const ys = (v) => padTop + (1 - (v - ymin) / (ymax - ymin)) * innerH;

  const parts = [`M${xs(meetings[0].t).toFixed(2)},${ys(meetings[0].v).toFixed(2)}`];
  for (let i = 1; i < meetings.length; i++) {
    const x = xs(meetings[i].t).toFixed(2);
    const prevY = ys(meetings[i - 1].v).toFixed(2);
    const y = ys(meetings[i].v).toFixed(2);
    parts.push(`L${x},${prevY}`, `L${x},${y}`);
  }
  return { d: parts.join(" "), xs, ys, padX, padTop, padBot, innerW, innerH };
}

const PolicyRateChart = ({ width = 800, height = 280 }) => {
  // 10-year history, monthly anchor points
  const start = new Date("2016-05-01").getTime();
  const monthMs = 30.44 * 24 * 3600 * 1000;
  // Stylised BoC overnight history
  const boc = [
    0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50,
    0.50, 0.50, 0.75, 0.75, 0.75, 0.75, 0.75, 1.00, 1.00, 1.00, 1.00, 1.00,
    1.25, 1.25, 1.25, 1.50, 1.50, 1.50, 1.50, 1.75, 1.75, 1.75, 1.75, 1.75,
    1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75,
    1.75, 1.75, 1.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
    0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
    0.25, 0.25, 0.50, 1.00, 1.50, 2.50, 3.25, 3.75, 4.25, 4.50, 4.50, 4.50,
    4.50, 4.50, 4.50, 4.50, 4.75, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00, 5.00,
    5.00, 5.00, 5.00, 5.00, 5.00, 4.75, 4.50, 4.25, 4.00, 3.75, 3.50, 3.25,
    3.00, 3.00, 2.75, 2.75, 2.75, 2.75, 2.75, 2.75, 2.75, 2.75, 2.75, 2.75
  ];
  const fed = [
    0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.75, 0.75, 0.75, 0.75, 0.75,
    1.00, 1.00, 1.25, 1.25, 1.50, 1.50, 1.75, 2.00, 2.00, 2.25, 2.25, 2.50,
    2.50, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50, 2.50, 2.25, 2.25, 2.00, 1.75,
    1.75, 1.75, 1.75, 1.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
    0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
    0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
    0.50, 0.75, 1.00, 1.75, 2.50, 3.25, 4.00, 4.50, 4.75, 5.00, 5.25, 5.50,
    5.50, 5.50, 5.50, 5.50, 5.50, 5.50, 5.50, 5.50, 5.50, 5.50, 5.50, 5.50,
    5.50, 5.50, 5.25, 5.00, 5.00, 4.75, 4.50, 4.25, 4.25, 4.25, 4.25, 4.25,
    4.25, 4.25, 4.25, 4.25, 4.25, 4.25, 4.25, 4.25, 4.25, 4.25, 4.25, 4.25
  ];
  const bocMeetings = boc.map((v, i) => ({ t: start + i * monthMs, v }));
  const fedMeetings = fed.map((v, i) => ({ t: start + i * monthMs, v }));

  const w = width, h = height;
  const ymin = 0, ymax = 6;
  const ticks = [0, 1, 2, 3, 4, 5];
  const bocCurve = genStepSeries(bocMeetings, w, h, ymin, ymax);
  const fedCurve = genStepSeries(fedMeetings, w, h, ymin, ymax);
  const { padX, padTop, padBot, innerW, innerH, xs, ys } = bocCurve;

  // Neutral band 2.25–3.25
  const bandTop = ys(3.25), bandBot = ys(2.25);

  // X-axis year labels (every 2 years)
  const yearLabels = [];
  for (let y = 2016; y <= 2026; y += 2) {
    const t = new Date(`${y}-05-01`).getTime();
    yearLabels.push({ x: xs(t), label: y });
  }

  return (
    <svg width={w} height={h} style={{ display: "block", overflow: "visible" }}>
      {/* gridlines + tick labels */}
      {ticks.map((tk) => (
        <g key={tk}>
          <line
            x1={padX}
            x2={w - 12}
            y1={ys(tk)}
            y2={ys(tk)}
            stroke="var(--rule)"
            strokeWidth="1"
          />
          <text
            x={padX - 8}
            y={ys(tk) + 3}
            textAnchor="end"
            style={{ font: "500 10px var(--font-mono)", fill: "var(--ink-quiet)" }}
          >
            {tk.toFixed(0)}
          </text>
        </g>
      ))}
      {/* neutral band */}
      <rect
        x={padX}
        y={bandTop}
        width={innerW}
        height={bandBot - bandTop}
        fill="var(--band-fill)"
      />
      {/* x-axis baseline */}
      <line
        x1={padX}
        x2={w - 12}
        y1={h - padBot}
        y2={h - padBot}
        stroke="var(--rule-strong)"
        strokeWidth="1"
      />
      {/* Fed (editorial overlay, dashed vermillion) */}
      <path
        d={fedCurve.d}
        fill="none"
        stroke="var(--vermillion)"
        strokeWidth="1.4"
        strokeDasharray="3 3"
        strokeLinejoin="round"
      />
      {/* BoC (primary cobalt) */}
      <path
        d={bocCurve.d}
        fill="none"
        stroke="var(--cobalt)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      {/* x labels */}
      {yearLabels.map((y) => (
        <text
          key={y.label}
          x={y.x}
          y={h - padBot + 16}
          textAnchor="middle"
          style={{ font: "500 10px var(--font-mono)", fill: "var(--ink-quiet)" }}
        >
          {y.label}
        </text>
      ))}
      {/* unit label top-left */}
      <text
        x={padX}
        y={padTop - 2}
        style={{ font: "500 10px var(--font-mono)", fill: "var(--ink-quiet)" }}
      >
        %
      </text>
      {/* current value annotation */}
      <g transform={`translate(${w - 12}, ${ys(2.75)})`}>
        <circle r="3" fill="var(--cobalt)" />
        <text x="-8" y="-8" textAnchor="end" style={{ font: "600 11px var(--font-mono)", fill: "var(--cobalt)" }}>2.75</text>
      </g>
      <g transform={`translate(${w - 12}, ${ys(4.25)})`}>
        <circle r="3" fill="var(--vermillion)" />
        <text x="-8" y="-8" textAnchor="end" style={{ font: "600 11px var(--font-mono)", fill: "var(--vermillion)" }}>4.25</text>
      </g>
      {/* band annotation */}
      <text
        x={padX + 8}
        y={ys(2.75) + 4}
        style={{ font: "500 10px var(--font-display)", fill: "var(--ink-quiet)" }}
      >
        neutral band 2.25 — 3.25
      </text>
    </svg>
  );
};

window.PolicyRateChart = PolicyRateChart;
