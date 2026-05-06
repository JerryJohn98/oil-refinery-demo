import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

 
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  safeUrl: SafeResourceUrl;

  constructor(private sanitizer: DomSanitizer) {
    this.safeUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
      'assets/OGDemoRecom/index.html'
    );
  }
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

    setInterval(() => {
      this.recalculate();
    }, 2000);
  }

  clamp(value: number, min: number, max: number) {
    return Math.min(max, Math.max(min, value));
  }

  randomStep(scale: number) {
    return (Math.random() * 2 - 1) * scale;
  }

  buildTicks(min: number, max: number) {
    const ticks = [];
    const steps = 8;

    for (let i = 0; i <= steps; i++) {
      ticks.push(Math.round(min + (i * (max - min)) / steps));
    }

    return ticks;
  }

  getTrendStatus(trend: number[]): string {
    if (trend.length < 2) return 'stable';
    const recent = trend.slice(-3);
    const older = trend.slice(-6, -3);
    const recentAvg = recent.reduce((a, b) => a + b) / recent.length;
    const olderAvg = older.length > 0 ? older.reduce((a, b) => a + b) / older.length : recentAvg;
    const diff = recentAvg - olderAvg;
    
    if (Math.abs(diff) < (Math.abs(olderAvg) * 0.01)) return 'stable';
    return diff > 0 ? 'up' : 'down';
  }

  toScaledPoints(values: number[], width: number, height: number, min: number, max: number) {
    const span = max - min || 1;

    return values.map((v, i) => {
      const x = (i / (values.length - 1)) * width;
      const y = height - ((v - min) / span) * (height - 6) - 3;
      return [x, y];
    });
  }

  pointsToLine(points: number[][]) {
    return points
      .map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`)
      .join(' ');
  }

  pointsToBand(upper: number[][], lower: number[][]) {
    const upperLine = this.pointsToLine(upper);

    const lowerLine = [...lower]
      .reverse()
      .map(([x, y]) => `L${x.toFixed(1)} ${y.toFixed(1)}`)
      .join(' ');

    return `${upperLine} ${lowerLine} Z`;
  }

  recalculate() {
    this.state.forEach(param => {

      const optimalRange = param.optimalHigh - param.optimalLow;
      const optimalCenter = (param.optimalLow + param.optimalHigh) / 2;

      const drift = this.randomStep(optimalRange * param.driftFactor);
      const pull = (optimalCenter - param.current) * 0.08;

      param.current = this.clamp(
        param.current + drift + pull,
        param.min,
        param.max
      );

      param.trend.push(param.current);
      if (param.trend.length > 20) {
        param.trend.shift();
      }

      const recommendedCenter = this.clamp(
        param.current + (optimalCenter - param.current) * 0.35,
        param.optimalLow,
        param.optimalHigh
      );

      const halfBand = optimalRange * param.bandFactor * 0.5;

      param.recommendedLower = this.clamp(
        recommendedCenter - halfBand,
        param.optimalLow,
        param.optimalHigh
      );

      param.recommendedUpper = this.clamp(
        recommendedCenter + halfBand,
        param.optimalLow,
        param.optimalHigh
      );

      param.confidence = Math.floor(Math.random() * 40 + 60);

      // 🔥 Sparkline generation
      const trendMin = Math.min(...param.trend);
      const trendMax = Math.max(...param.trend);

      const spread = (trendMax - trendMin) * 0.15;

      const upper = param.trend.map(v => v + spread);
      const lower = param.trend.map(v => v - spread);

      const scaleMin = Math.min(...lower);
      const scaleMax = Math.max(...upper);

      const trendPoints = this.toScaledPoints(param.trend, 280, 72, scaleMin, scaleMax);
      const upperPoints = this.toScaledPoints(upper, 280, 72, scaleMin, scaleMax);
      const lowerPoints = this.toScaledPoints(lower, 280, 72, scaleMin, scaleMax);

      param.linePath = this.pointsToLine(trendPoints);
      param.bandPath = this.pointsToBand(upperPoints, lowerPoints);

      param.lastUpdated = new Date().toLocaleTimeString();
      param.trendStatus = this.getTrendStatus(param.trend);
    });

    this.updateKpis();
  }

  updateKpis() {
    const avgConfidence =
      this.state.reduce((sum, p) => sum + p.confidence, 0) / this.state.length;

    this.kpiEfficiency = Math.round(70 + avgConfidence * 0.3);
    this.kpiYield = Math.round(111 + avgConfidence * 0.5);
    this.kpiRisk = Math.round(100 - avgConfidence);
    this.kpiEnergy = +(0.92 - Math.random() * 0.1).toFixed(2);
  }
}