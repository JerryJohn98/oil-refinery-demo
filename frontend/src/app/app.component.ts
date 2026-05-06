import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  state: any[] = [];

  kpiEfficiency = 0;
  kpiYield = 0;
  kpiRisk = 0;
  kpiEnergy = 0;

  parameters = [
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
      trend: [2580, 2610, 2640, 2665, 2685],
      driftFactor: 0.018,
      bandFactor: 0.16,
      confidence: 90
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
      trend: [19800, 20350, 20820, 21100, 21450],
      driftFactor: 0.015,
      bandFactor: 0.14,
      confidence: 92
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
      trend: [2710, 2760, 2800, 2835, 2860],
      driftFactor: 0.017,
      bandFactor: 0.15,
      confidence: 91
    }
  ];

  ngOnInit(): void {
    this.state = this.parameters;

    this.state.forEach(p => {
      p.ticks = this.buildTicks(p.min, p.max);
    });

    this.recalculate();

    setInterval(() => this.recalculate(), 2000);
  }

  clamp(v: number, min: number, max: number) {
    return Math.min(max, Math.max(min, v));
  }

  randomStep(scale: number) {
    return (Math.random() * 2 - 1) * scale;
  }

  buildTicks(min: number, max: number) {
    const ticks = [];
    for (let i = 0; i <= 8; i++) {
      ticks.push(Math.round(min + (i * (max - min)) / 8));
    }
    return ticks;
  }

  getTrendStatus(trend: number[]) {
    const slope = trend[trend.length - 1] - trend[Math.max(0, trend.length - 4)];

    if (slope > 0) return { label: 'rising', class: 'trend-up' };
    if (slope < 0) return { label: 'falling', class: 'trend-down' };
    return { label: 'stable', class: 'trend-flat' };
  }

  getConstraint(param: any) {
    if (param.current > param.optimalHigh * 0.98) {
      return { label: 'Hydraulic limit near', class: 'constraint-critical' };
    }
    if (param.current < param.optimalLow * 1.01) {
      return { label: 'Under-injection risk', class: 'constraint-warn' };
    }
    return { label: 'Within constraints', class: 'constraint-ok' };
  }

  toScaledPoints(values: number[], w: number, h: number, min: number, max: number) {
    const span = max - min || 1;
    return values.map((v, i) => [
      (i / (values.length - 1)) * w,
      h - ((v - min) / span) * (h - 6) - 3
    ]);
  }

  pointsToLine(points: number[][]) {
    return points.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  }

  pointsToBand(upper: number[][], lower: number[][]) {
    return `${this.pointsToLine(upper)} ${[...lower].reverse().map(([x,y])=>`L${x.toFixed(1)} ${y.toFixed(1)}`).join(' ')} Z`;
  }

  recalculate() {
    this.state.forEach(param => {

      const range = param.optimalHigh - param.optimalLow;
      const center = (param.optimalLow + param.optimalHigh) / 2;

      param.current = this.clamp(
        param.current + this.randomStep(range * param.driftFactor) + (center - param.current) * 0.08,
        param.min,
        param.max
      );

      param.trend.push(param.current);
      if (param.trend.length > 20) param.trend.shift();

      const recCenter = this.clamp(param.current + (center - param.current) * 0.35, param.optimalLow, param.optimalHigh);
      const band = range * param.bandFactor * 0.5;

      param.recommendedLower = this.clamp(recCenter - band, param.optimalLow, param.optimalHigh);
      param.recommendedUpper = this.clamp(recCenter + band, param.optimalLow, param.optimalHigh);

      param.confidence = Math.floor(Math.random() * 40 + 60);

      // ✅ DELTA
      const target = (param.recommendedLower + param.recommendedUpper) / 2;
      const delta = target - param.current;

      const sign = delta > 0 ? '+' : '';
      param.deltaText = Math.abs(delta) < 0.1 ? 'On target' : `${sign}${delta.toFixed(2)} ${param.unit}`;

      if (Math.abs(delta) < 0.1) param.deltaClass = 'delta-neutral';
      else if (delta > 0) param.deltaClass = 'delta-positive';
      else param.deltaClass = 'delta-negative';

      // ✅ CONSTRAINT
      const c = this.getConstraint(param);
      param.constraintLabel = c.label;
      param.constraintClass = c.class;

      // ✅ TREND
      const t = this.getTrendStatus(param.trend);
      param.trendLabel = t.label;
      param.trendClass = t.class;

      // ✅ SPARKLINE
      const min = Math.min(...param.trend);
      const max = Math.max(...param.trend);
      const spread = (max - min) * 0.15;

      const upper = param.trend.map(v => v + spread);
      const lower = param.trend.map(v => v - spread);

      const sMin = Math.min(...lower);
      const sMax = Math.max(...upper);

      param.linePath = this.pointsToLine(this.toScaledPoints(param.trend, 280, 72, sMin, sMax));
      param.bandPath = this.pointsToBand(
        this.toScaledPoints(upper, 280, 72, sMin, sMax),
        this.toScaledPoints(lower, 280, 72, sMin, sMax)
      );

      param.lastUpdated = new Date().toLocaleTimeString();
    });

    this.updateKpis();
  }

  updateKpis() {
    const avg = this.state.reduce((s, p) => s + p.confidence, 0) / this.state.length;

    this.kpiEfficiency = Math.round(70 + avg * 0.3);
    this.kpiYield = Math.round(100 + avg);
    this.kpiRisk = Math.round(100 - avg);
    this.kpiEnergy = +(0.9 + Math.random() * 0.1).toFixed(2);
  }
}