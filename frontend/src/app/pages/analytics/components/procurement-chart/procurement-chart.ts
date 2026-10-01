import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { ChartConfiguration } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { AnalyticsService } from '../../../../services/analytics.service';

@Component({
  selector: 'app-procurement-chart',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    BaseChartDirective
  ],
  templateUrl: './procurement-chart.html',
  styleUrl: './procurement-chart.css'
})
export class ProcurementChart implements OnInit {
  private analyticsService = inject(AnalyticsService);
  private cdr = inject(ChangeDetectorRef);

  hasData = false;

  lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: [],
    datasets: [
      {
        label: 'Procurement Spend',
        data: [],
        tension: 0.4,
        fill: false
      }
    ]
  };

  lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false
  };

  ngOnInit(): void {
    this.analyticsService.getProcurementAnalytics().subscribe({
      next: (data) => {
        const trend = data.monthly_spend_trend ?? [];
        const labels = trend.map((t: any) => t.month);
        const amounts = trend.map((t: any) => Number(t.total_amount ?? 0));

        if (labels.length > 0 && amounts.some((a: number) => a > 0)) {
          this.hasData = true;
          this.lineChartData = {
            labels: labels,
            datasets: [
              {
                label: 'Procurement Spend ($)',
                data: amounts,
                tension: 0.4,
                fill: false,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
              }
            ]
          };
        } else {
          this.hasData = false;
          this.lineChartData = {
            labels: [],
            datasets: []
          };
        }
        this.cdr.markForCheck();
      },
      error: () => {
        this.hasData = false;
        this.lineChartData = { labels: [], datasets: [] };
        this.cdr.markForCheck();
      }
    });
  }
}