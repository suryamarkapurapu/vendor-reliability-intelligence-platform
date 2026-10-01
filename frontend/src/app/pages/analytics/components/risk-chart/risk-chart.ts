import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { ChartConfiguration } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { VendorPerformanceService } from '../../../../services/vendor-performance.service';

@Component({
  selector: 'app-risk-chart',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    BaseChartDirective
  ],
  templateUrl: './risk-chart.html',
  styleUrl: './risk-chart.css'
})
export class RiskChart implements OnInit {
  private vendorPerformanceService = inject(VendorPerformanceService);
  private cdr = inject(ChangeDetectorRef);

  hasData = false;

  doughnutChartData: ChartConfiguration<'doughnut'>['data'] = {
    labels: [],
    datasets: []
  };

  doughnutChartOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    maintainAspectRatio: false
  };

  ngOnInit(): void {
    this.vendorPerformanceService.getRankings(0, 100).subscribe({
      next: (rankings) => {
        let low = 0;
        let medium = 0;
        let high = 0;

        rankings.forEach((r: any) => {
          const score = Number(r.overall_score ?? 0);
          if (score >= 80) {
            low++;
          } else if (score >= 60) {
            medium++;
          } else {
            high++;
          }
        });

        if (low + medium + high > 0) {
          this.hasData = true;
          this.doughnutChartData = {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [
              {
                data: [low, medium, high],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
              }
            ]
          };
        } else {
          this.hasData = false;
          this.doughnutChartData = { labels: [], datasets: [] };
        }
        this.cdr.markForCheck();
      },
      error: () => {
        this.hasData = false;
        this.doughnutChartData = { labels: [], datasets: [] };
        this.cdr.markForCheck();
      }
    });
  }
}