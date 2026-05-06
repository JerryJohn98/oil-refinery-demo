import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  state: any[] = [];

  kpiEfficiency = 0;
  kpiUplift = 0;
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
      confidence: 0
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
      confidence: 0
    }
  ];

  ngOnInit(): void {
    this.state = this.parameters;
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

  recalculate() {
    this.state.forEach(param => {
      const optimalRange = param.optimalHigh - param.optimalLow;
      const optimalCenter = (param.optimalLow + param.optimalHigh) / 2;

      const drift = this.randomStep(optimalRange * param.driftFactor);
      const pull = (optimalCenter - param.current) * 0.08;

      param.current = this.clamp(param.current + drift + pull, param.min, param.max);

      param.trend.push(param.current);
      if (param.trend.length > 20) param.trend.shift();

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
    });

    this.updateKpis();
  }

  updateKpis() {
    const avgConfidence =
      this.state.reduce((sum, p) => sum + p.confidence, 0) / this.state.length;

    this.kpiEfficiency = Math.round(70 + avgConfidence * 0.3);
    this.kpiUplift = Math.round(avgConfidence * 2);
    this.kpiRisk = Math.round(100 - avgConfidence);
    this.kpiEnergy = +(Math.random() * 1).toFixed(2);
  }
}