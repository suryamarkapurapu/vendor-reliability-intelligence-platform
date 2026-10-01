import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartType } from 'chart.js';

@Component({
  selector: 'app-chart-card',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    BaseChartDirective
  ],
  templateUrl: './chart-card.html',
  styleUrl: './chart-card.css'
})
export class ChartCard {
  @Input() title = '';
  @Input() chartType: ChartType = 'bar';
  @Input() chartData: ChartConfiguration['data'] = {
    labels: [],
    datasets: []
  };

  chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  get hasData(): boolean {
    if (!this.chartData || !this.chartData.labels || this.chartData.labels.length === 0) {
      return false;
    }
    const ds = this.chartData.datasets;
    if (!ds || ds.length === 0) return false;
    return ds.some(d => d.data && d.data.length > 0 && d.data.some((val: any) => Number(val) > 0));
  }
}