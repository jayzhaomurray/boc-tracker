/* eslint-disable */
// Sparklines + small chart primitives, hand-drawn SVG.

// Build a path from y-values normalised to a [0,1] box.
function buildPath(ys, w, h, pad = 2) {
  const n = ys.length;
  const min = Math.min(...ys);
  const max = Math.max(...ys);
  const range = max - min || 1;
  const innerH = h - pad * 2;
  return ys
    .map((y, i) => {
      const x = (i / (n - 1)) * w;
      const norm = (y - min) / range;
      const py = pad + (1 - norm) * innerH;
      return `${i === 0 ? "M" : "L"}${x.toFixed(2)},${py.toFixed(2)}`;
    })
    .join(" ");
}

const Sparkline = ({ data, color = "var(--cobalt)", width = 120, height = 32, dash = false }) => {
  const d = buildPath(data, width, height, 3);
  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={dash ? "3 3" : undefined}
      />
    </svg>
  );
};

window.Sparkline = Sparkline;
window.buildPath = buildPath;
