/* eslint-disable */
// CPIComponentsChart — multi-line, categorical palette.
// Headline + Food + Energy + Goods + Services.

function buildLinePath(values, w, h, ymin, ymax, padX, padTop, padBot) {
  const innerW = w - padX - 12;
  const innerH = h - padTop - padBot;
  const n = values.length;
  return values
    .map((v, i) => {
      const x = padX + (i / (n - 1)) * innerW;
      const y = padTop + (1 - (v - ymin) / (ymax - ymin)) * innerH;
      return `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}

const CPIComponentsChart = ({ width = 800, height = 260, visible = ["headline", "food", "energy"] }) => {
  // 10-year monthly Y/Y, stylised
  const headline = [1.5, 1.4, 1.3, 1.3, 1.5, 1.6, 1.5, 1.4, 1.5, 1.5, 1.4, 1.4,
    1.6, 1.7, 2.0, 2.4, 2.5, 2.5, 2.3, 2.0, 1.9, 1.7, 1.7, 1.9,
    2.0, 2.2, 2.4, 2.1, 1.9, 1.7, 1.4, 1.3, 1.2, 1.3, 1.3, 1.3,
    0.9, 0.8, 0.7, 0.6, 0.5, 0.8, 1.1, 1.4, 1.7, 2.2, 2.4, 3.4,
    4.1, 4.7, 5.0, 5.5, 6.1, 6.8, 7.1, 6.9, 6.5, 6.0, 5.4, 4.8,
    4.4, 4.0, 3.5, 3.3, 3.1, 2.9, 2.8, 2.7, 2.7, 2.6, 2.5, 2.3,
    2.2, 2.0, 1.8, 1.7, 1.6, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2,
    2.2, 2.3, 2.3, 2.3, 2.3, 2.2, 2.3, 2.3];
  const food = [2.4, 2.5, 2.7, 2.8, 2.5, 2.2, 1.9, 1.7, 1.6, 1.5, 1.5, 1.6,
    1.7, 1.9, 2.1, 2.4, 2.5, 2.6, 2.6, 2.7, 2.8, 2.7, 2.5, 2.3,
    2.0, 1.8, 1.7, 1.7, 1.6, 1.5, 1.3, 1.4, 1.5, 1.6, 1.7, 1.7,
    1.8, 1.6, 1.4, 1.5, 1.4, 1.5, 1.4, 1.6, 1.8, 2.4, 3.1, 4.0,
    5.4, 7.0, 8.5, 9.4, 10.1, 10.6, 10.4, 9.8, 8.9, 7.8, 6.6, 5.5,
    4.7, 4.0, 3.4, 3.1, 2.9, 2.7, 2.6, 2.5, 2.5, 2.4, 2.3, 2.2,
    2.1, 2.0, 1.9, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.5, 2.5,
    2.5, 2.6, 2.7, 2.7, 2.7, 2.6, 2.5, 2.5];
  const energy = [-1.0, -3.0, -4.5, -3.0, 1.0, 4.0, 6.0, 8.0, 5.0, 4.0, 6.0, 7.0,
    8.0, 9.0, 11.0, 12.0, 13.0, 12.0, 10.0, 6.0, 4.0, 2.0, 1.5, 1.0,
    2.0, 3.0, 4.0, 3.0, 2.0, 0.5, -1.0, -2.0, -2.5, -3.0, -4.0, -3.5,
    -8.0, -10.0, -12.0, -16.0, -22.0, -10.0, -2.0, 5.0, 12.0, 16.0, 18.0, 22.0,
    28.0, 35.0, 42.0, 40.0, 38.0, 34.0, 28.0, 22.0, 14.0, 6.0, 0.0, -4.0,
    -6.0, -8.0, -10.0, -8.0, -4.0, 0.0, 3.0, 4.0, 5.0, 6.0, 5.0, 4.0,
    3.0, 2.0, 1.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 5.5, 6.0, 6.5,
    6.5, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5];
  const goods = [0.4, 0.3, 0.3, 0.4, 0.5, 0.5, 0.6, 0.7, 0.7, 0.8, 0.7, 0.7,
    0.8, 0.9, 1.0, 1.2, 1.3, 1.3, 1.2, 1.1, 1.1, 1.0, 1.0, 1.1,
    1.2, 1.2, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6, 0.6, 0.5, 0.5,
    0.4, 0.3, 0.2, 0.3, 0.4, 0.7, 1.2, 1.8, 2.4, 3.0, 3.6, 4.5,
    5.4, 6.3, 7.0, 7.6, 8.0, 8.3, 8.0, 7.5, 6.8, 6.0, 5.2, 4.5,
    4.0, 3.6, 3.2, 3.0, 2.7, 2.5, 2.3, 2.1, 2.0, 1.9, 1.8, 1.7,
    1.6, 1.5, 1.4, 1.4, 1.5, 1.5, 1.6, 1.7, 1.8, 1.8, 1.9, 1.9,
    2.0, 2.0, 2.0, 2.0, 1.9, 1.9, 1.9, 1.8];
  const services = [2.2, 2.3, 2.3, 2.4, 2.4, 2.4, 2.3, 2.2, 2.2, 2.1, 2.1, 2.0,
    2.0, 2.1, 2.2, 2.3, 2.4, 2.4, 2.4, 2.5, 2.5, 2.6, 2.6, 2.7,
    2.8, 2.9, 2.9, 2.9, 2.8, 2.8, 2.7, 2.6, 2.5, 2.4, 2.4, 2.3,
    2.0, 1.8, 1.6, 1.5, 1.5, 1.6, 1.7, 1.9, 2.1, 2.4, 2.8, 3.2,
    3.6, 4.0, 4.3, 4.6, 4.8, 5.0, 5.1, 5.0, 4.9, 4.7, 4.5, 4.3,
    4.1, 4.0, 3.9, 3.8, 3.7, 3.6, 3.5, 3.4, 3.3, 3.2, 3.2, 3.1,
    3.0, 2.9, 2.8, 2.7, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6,
    2.6, 2.6, 2.6, 2.6, 2.5, 2.5, 2.5, 2.4];

  const series = [
    { id: "headline", values: headline, color: "var(--cobalt)", width: 2 },
    { id: "food",     values: food,     color: "var(--cat-pine)", width: 1.4 },
    { id: "energy",   values: energy,   color: "var(--cat-amber)", width: 1.4 },
    { id: "goods",    values: goods,    color: "var(--cat-teal)", width: 1.4 },
    { id: "services", values: services, color: "var(--cat-plum)", width: 1.4 },
  ];

  const visSeries = series.filter((s) => visible.includes(s.id));
  const allVals = visSeries.flatMap((s) => s.values);
  let ymin = Math.floor(Math.min(...allVals) / 2) * 2;
  let ymax = Math.ceil(Math.max(...allVals) / 2) * 2;
  if (ymax - ymin < 5) ymax = ymin + 5;

  const w = width, h = height;
  const padX = 36, padTop = 14, padBot = 26;
  const innerW = w - padX - 12, innerH = h - padTop - padBot;

  // 5 round ticks
  const tickStep = (ymax - ymin) / 5;
  const ticks = [];
  for (let i = 0; i <= 5; i++) ticks.push(ymin + i * tickStep);

  // Year labels
  const start = 2016;
  const yearLabels = [];
  for (let yr = start; yr <= 2026; yr += 2) {
    const idx = (yr - start) * 12;
    yearLabels.push({ x: padX + (idx / 119) * innerW, label: yr });
  }

  return (
    <svg width={w} height={h} style={{ display: "block", overflow: "visible" }}>
      {/* gridlines */}
      {ticks.map((t, i) => (
        <g key={i}>
          <line
            x1={padX}
            x2={w - 12}
            y1={padTop + (1 - (t - ymin) / (ymax - ymin)) * innerH}
            y2={padTop + (1 - (t - ymin) / (ymax - ymin)) * innerH}
            stroke="var(--rule)"
            strokeWidth="1"
            strokeDasharray={t === 0 ? "0" : t === 2 ? "0" : "0"}
          />
          <text
            x={padX - 8}
            y={padTop + (1 - (t - ymin) / (ymax - ymin)) * innerH + 3}
            textAnchor="end"
            style={{ font: "500 10px var(--font-mono)", fill: "var(--ink-quiet)" }}
          >
            {Math.round(t)}
          </text>
        </g>
      ))}
      {/* 2% target reference line */}
      {ymin <= 2 && ymax >= 2 && (
        <line
          x1={padX}
          x2={w - 12}
          y1={padTop + (1 - (2 - ymin) / (ymax - ymin)) * innerH}
          y2={padTop + (1 - (2 - ymin) / (ymax - ymin)) * innerH}
          stroke="var(--rule-emphasis)"
          strokeWidth="1"
          strokeDasharray="2 4"
          opacity="0.5"
        />
      )}
      {visSeries.map((s) => (
        <path
          key={s.id}
          d={buildLinePath(s.values, w, h, ymin, ymax, padX, padTop, padBot)}
          fill="none"
          stroke={s.color}
          strokeWidth={s.width}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      ))}
      <text x={padX} y={padTop - 2} style={{ font: "500 10px var(--font-mono)", fill: "var(--ink-quiet)" }}>
        % Y/Y
      </text>
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
    </svg>
  );
};

window.CPIComponentsChart = CPIComponentsChart;
