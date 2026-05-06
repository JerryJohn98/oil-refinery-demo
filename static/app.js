const parameters = [
  {
    name: "Water Injection Header Pressure",
    unit: "psi",
    min: 1500,
    max: 4200,
    optimalLow: 2350,
    optimalHigh: 3150,
    current: 2685,
    recommendedLower: 2620,
    recommendedUpper: 2795,
    trendSeed: [2580, 2610, 2640, 2665, 2685],
    driftFactor: 0.018,
    bandFactor: 0.16
  },
  {
    name: "Produced Water Injection Rate",
    unit: "bwpd",
    min: 5000,
    max: 45000,
    optimalLow: 19000,
    optimalHigh: 30000,
    current: 21450,
    recommendedLower: 20900,
    recommendedUpper: 22650,
    trendSeed: [19800, 20350, 20820, 21100, 21450],
    driftFactor: 0.015,
    bandFactor: 0.14
  },
  {
    name: "Wellhead Injection Pressure",
    unit: "psi",
    min: 1200,
    max: 4500,
    optimalLow: 2100,
    optimalHigh: 3350,
    current: 2860,
    recommendedLower: 2790,
    recommendedUpper: 2980,
    trendSeed: [2710, 2760, 2800, 2835, 2860],
    driftFactor: 0.017,
    bandFactor: 0.15
  }
];

const dashboard = document.getElementById("dashboard");
const template = document.getElementById("parameterTemplate");
const kpiEfficiency = document.getElementById("kpiEfficiency");
const kpiUplift = document.getElementById("kpiUplift");
const kpiRisk = document.getElementById("kpiRisk");
const kpiEnergy = document.getElementById("kpiEnergy");

const state = parameters.map((param) => ({
  ...param,
  trend: [...param.trendSeed],
  confidence: 0
}));

function round(value, digits = 2) {
  return Number.parseFloat(value).toFixed(digits);
}

function randomStep(scale) {
  return (Math.random() * 2 - 1) * scale;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function toScaledPoints(values, width, height, scaleMin, scaleMax) {
  const span = scaleMax - scaleMin || 1;
  return values.map((value, index) => {
    const x = (index / (values.length - 1)) * width;
    const y = height - ((value - scaleMin) / span) * (height - 6) - 3;
    return [x, y];
  });
}

function pointsToLine(points) {
  return points
    .map(([x, y], index) => `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(" ");
}

function pointsToBand(upperPoints, lowerPoints) {
  const upperLine = pointsToLine(upperPoints);
  const lowerReturn = [...lowerPoints]
    .reverse()
    .map(([x, y]) => `L${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(" ");
  return `${upperLine} ${lowerReturn} Z`;
}

function scoreConfidence(param) {
  const center = (param.optimalLow + param.optimalHigh) / 2;
  const range = param.max - param.min;
  const optimalWidth = param.optimalHigh - param.optimalLow;
  const recent = param.trend.slice(-6);
  const recentSpread = Math.max(...recent) - Math.min(...recent);

  const distancePenalty = Math.abs(param.current - center) / (range / 2);
  const spreadPenalty = (param.recommendedUpper - param.recommendedLower) / optimalWidth;
  const stabilityPenalty = clamp(recentSpread / optimalWidth, 0, 1);

  const raw = 1 - (distancePenalty * 0.5 + spreadPenalty * 0.3 + stabilityPenalty * 0.2);
  return clamp(Math.round(raw * 100), 45, 98);
}

function buildTicks(min, max) {
  const ticks = [];
  const steps = 8;
  for (let i = 0; i <= steps; i += 1) {
    const value = min + (i * (max - min)) / steps;
    ticks.push(Math.round(value));
  }
  return ticks;
}

function trendClassAndLabel(trend) {
  const n = trend.length;
  const slope = trend[n - 1] - trend[Math.max(0, n - 4)];

  if (slope > 0.12 * Math.max(1, trend[n - 1])) {
    return { className: "trend-up", label: "rising" };
  }

  if (slope < -0.12 * Math.max(1, trend[n - 1])) {
    return { className: "trend-down", label: "falling" };
  }

  return { className: "trend-flat", label: "stable" };
}

function pointsToPath(values, width, height, asArea = false) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;

  const points = values.map((v, i) => {
    const x = (i / (values.length - 1)) * width;
    const y = height - ((v - min) / span) * (height - 6) - 3;
    return [x, y];
  });

  const line = points.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");

  if (!asArea) {
    return line;
  }

  const [firstX] = points[0];
  const [lastX] = points[points.length - 1];
  return `${line} L${lastX.toFixed(1)} ${height} L${firstX.toFixed(1)} ${height} Z`;
}

function getConstraintStatus(param) {
  const optimalSpan = param.optimalHigh - param.optimalLow;
  const recent = param.trend.slice(-6);
  const instability = Math.max(...recent) - Math.min(...recent);

  if (param.current > param.optimalHigh * 0.98) {
    return { label: "Hydraulic limit near", className: "constraint-critical" };
  }

  if (param.current < param.optimalLow * 1.01) {
    return { label: "Under-injection risk", className: "constraint-warn" };
  }

  if (instability > optimalSpan * 0.22) {
    return { label: "Response unstable", className: "constraint-warn" };
  }

  return { label: "Within constraints", className: "constraint-ok" };
}

function updateKpis() {
  const avgConfidence = state.reduce((acc, item) => acc + item.confidence, 0) / state.length;
  const rate = state.find((item) => item.name === "Produced Water Injection Rate");
  const headerPressure = state.find((item) => item.name === "Water Injection Header Pressure");
  const wellPressure = state.find((item) => item.name === "Wellhead Injection Pressure");

  const rateTarget = (rate.recommendedLower + rate.recommendedUpper) / 2;
  const efficiency = clamp(100 - (Math.abs(rate.current - rateTarget) / (rate.optimalHigh - rate.optimalLow)) * 110, 64, 99);

  const uplift = clamp((avgConfidence - 65) * 2.6 + (efficiency - 75) * 1.4, 25, 240);

  const pressureStress = clamp((headerPressure.current / headerPressure.optimalHigh) * 45 + (wellPressure.current / wellPressure.optimalHigh) * 45, 0, 100);
  const riskValue = Math.round(clamp(pressureStress + (100 - avgConfidence) * 0.55, 8, 95));

  const totalPressure = headerPressure.current + wellPressure.current;
  const energy = clamp(totalPressure / (rate.current / 1000) * 0.06, 0.08, 0.92);

  kpiEfficiency.textContent = `${Math.round(efficiency)}%`;
  kpiUplift.textContent = `+${Math.round(uplift)} bopd`;
  kpiRisk.textContent = `${riskValue}%`;
  kpiEnergy.textContent = `${energy.toFixed(2)} kWh/bbl`;
}

function renderCard(param) {
  const node = template.content.firstElementChild.cloneNode(true);

  node.querySelector(".param-name").textContent = param.name;
  node.querySelector(".rec-title").textContent = `Setpoint Recommendation: ${param.name}`;
  node.querySelector(".last-refresh").textContent = `Last refreshed ${new Date().toLocaleTimeString()}`;

  updateSingleCard(node, param);
  return node;
}

function updateSingleCard(node, param) {
  node.querySelector(".actual-label").textContent = `${round(param.current)}`;
  node.querySelector(".units-label").textContent = `Actual ${param.unit}`;
  node.querySelector(".rec-lower").textContent = `${round(param.recommendedLower)}`;
  node.querySelector(".rec-upper").textContent = `${round(param.recommendedUpper)}`;

  const needlePercent = ((param.current - param.min) / (param.max - param.min)) * 100;
  node.querySelector(".needle").style.left = `${clamp(needlePercent, 0, 100)}%`;

  const ticks = buildTicks(param.min, param.max);
  const tickRow = node.querySelector(".tick-row");
  tickRow.innerHTML = "";
  ticks.forEach((tick) => {
    const span = document.createElement("span");
    span.textContent = tick;
    tickRow.appendChild(span);
  });

  const confidenceScore = node.querySelector(".confidence-score");
  confidenceScore.textContent = `${param.confidence}%`;
  const confidenceFill = node.querySelector(".confidence-fill");
  confidenceFill.style.width = `${param.confidence}%`;

  const targetCenter = (param.recommendedLower + param.recommendedUpper) / 2;
  const delta = targetCenter - param.current;
  const deltaValue = node.querySelector(".delta-value");
  const sign = delta > 0.1 ? "+" : "";
  const deltaMagnitude = Math.abs(delta) < 0.1 ? "On target" : `${sign}${round(delta)} ${param.unit}`;
  deltaValue.textContent = deltaMagnitude;
  deltaValue.className = "delta-value";
  if (Math.abs(delta) < 0.1) {
    deltaValue.classList.add("delta-neutral");
  } else if (delta > 0) {
    deltaValue.classList.add("delta-positive");
  } else {
    deltaValue.classList.add("delta-negative");
  }

  const { label: constraintLabel, className: constraintClass } = getConstraintStatus(param);
  const constraintBadge = node.querySelector(".constraint-badge");
  constraintBadge.textContent = constraintLabel;
  constraintBadge.className = `constraint-badge ${constraintClass}`;

  const { className, label } = trendClassAndLabel(param.trend);
  const trendTag = node.querySelector(".trend-tag");
  trendTag.className = `trend-tag ${className}`;
  trendTag.textContent = label;

  const line = node.querySelector(".sparkline-line");
  const band = node.querySelector(".sparkline-band");
  const trendMin = Math.min(...param.trend);
  const trendMax = Math.max(...param.trend);
  const baseBand = Math.max((trendMax - trendMin) * 0.11, Math.max(1, param.current * 0.004));
  const confidenceFactor = (100 - param.confidence) / 100;
  const spread = baseBand * (1 + confidenceFactor * 2.1);
  const upper = param.trend.map((value) => value + spread);
  const lower = param.trend.map((value) => value - spread);

  const scaleMin = Math.min(...lower);
  const scaleMax = Math.max(...upper);
  const trendPoints = toScaledPoints(param.trend, 280, 72, scaleMin, scaleMax);
  const upperPoints = toScaledPoints(upper, 280, 72, scaleMin, scaleMax);
  const lowerPoints = toScaledPoints(lower, 280, 72, scaleMin, scaleMax);

  line.setAttribute("d", pointsToLine(trendPoints));
  band.setAttribute("d", pointsToBand(upperPoints, lowerPoints));
}

function renderDashboard() {
  dashboard.innerHTML = "";
  state.forEach((param) => {
    const node = renderCard(param);
    dashboard.appendChild(node);
  });
}

function recalculate() {
  state.forEach((param, idx) => {
    const optimalRange = param.optimalHigh - param.optimalLow;
    const optimalCenter = (param.optimalLow + param.optimalHigh) / 2;

    const drift = randomStep(optimalRange * param.driftFactor);
    const pullToCenter = (optimalCenter - param.current) * 0.08;

    param.current = clamp(param.current + drift + pullToCenter, param.min, param.max);
    param.trend.push(param.current);
    if (param.trend.length > 22) {
      param.trend.shift();
    }

    const recommendedCenter = clamp(param.current + (optimalCenter - param.current) * 0.35, param.optimalLow, param.optimalHigh);
    const halfBand = optimalRange * param.bandFactor * 0.5;

    param.recommendedLower = clamp(recommendedCenter - halfBand, param.optimalLow, param.optimalHigh);
    param.recommendedUpper = clamp(recommendedCenter + halfBand, param.optimalLow, param.optimalHigh);

    param.confidence = scoreConfidence(param);

    const card = dashboard.children[idx];
    if (card) {
      card.querySelector(".last-refresh").textContent = `Last refreshed ${new Date().toLocaleTimeString()}`;
      updateSingleCard(card, param);
    }
  });

  updateKpis();
}

renderDashboard();
recalculate();
setInterval(recalculate, 2000);
