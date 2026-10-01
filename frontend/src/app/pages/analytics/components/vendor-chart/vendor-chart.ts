import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { ChartConfiguration } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { AnalyticsService } from '../../../../services/analytics.service';

@Component({
  selector: 'app-vendor-chart',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    BaseChartDirective
  ],
  templateUrl: './vendor-chart.html',
  styleUrl: './vendor-chart.css'
})
export class VendorChart implements OnInit {
  private analyticsService = inject(AnalyticsService);
  private cdr = inject(ChangeDetectorRef);

  hasData = false;

  barChartData: ChartConfiguration<'bar'>['data'] = {
    labels: [],
    datasets: [
      {
        label: 'Vendor Spend ($)',
        data: []
      }
    ]
  };

  barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false
  };

  ngOnInit(): void {
    this.analyticsService.getVendorAnalytics().subscribe({
      next: (data) => {
        const top = data.top_vendors_by_spend ?? [];
        const labels = top.map((v: any) => v.vendor_name);
        const spend = top.map((v: any) => Number(v.total_spend ?? 0));

        if (labels.length > 0 && spend.some((s: number) => s > 0)) {
          this.hasData = true;
          this.barChartData = {
            labels: labels,
            datasets: [
              {
                label: 'Vendor Spend ($)',
                data: spend,
                backgroundColor: '#3b82f6'
              }
            ]
          };
        } else {
          this.hasData = false;
          this.barChartData = {
            labels: [],
            datasets: []
          };
        }
        this.cdr.markForCheck();
      },
      error: () => {
        this.hasData = false;
        this.barChartData = { labels: [], datasets: [] };
        this.cdr.markForCheck();
      }
    });
  }
}