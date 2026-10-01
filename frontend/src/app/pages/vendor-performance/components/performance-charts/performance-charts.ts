import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import { VendorPerformanceService } from '../../../../services/vendor-performance.service';

@Component({
  selector: 'app-performance-charts',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    BaseChartDirective
  ],
  templateUrl: './performance-charts.html',
  styleUrl: './performance-charts.css'
})
export class PerformanceCharts implements OnInit {
  private performanceService = inject(VendorPerformanceService);
  private cdr = inject(ChangeDetectorRef);

  hasBreakdownData = false;
  hasTrendData = false;

  // Performance Breakdown
  performanceChartType: 'bar' = 'bar';
  performanceChartData: ChartData<'bar'> = {
    labels: [],
    datasets: []
  };

  performanceChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    scales: {
      x: {
        beginAtZero: true,
        max: 100
      }
    },
    plugins: {
      legend: {
        display: false
      }
    }
  };

  // Performance Trend
  trendChartType: 'line' = 'line';
  trendChartData: ChartData<'line'> = {
    labels: [],
    datasets: []
  };

  trendChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    }
  };

  ngOnInit(): void {
    this.loadChartData();
  }

  loadChartData(): void {
    this.performanceService.getRankings().subscribe({
      next: (rankings) => {
        if (rankings && rankings.length > 0) {
          const avgDelivery = Math.round(rankings.reduce((sum, r) => sum + Number(r.on_time_delivery_rate || 0), 0) / rankings.length);
          const avgQuality = Math.round((rankings.reduce((sum, r) => sum + Number(r.average_overall_rating || 0), 0) / rankings.length) * 20);
          const avgOverall = Math.round(rankings.reduce((sum, r) => sum + Number(r.overall_score || 0), 0) / rankings.length);

          this.performanceChartData = {
            labels: ['Delivery', 'Quality', 'Overall Reliability'],
            datasets: [
              {
                label: 'Performance Score',
                data: [avgDelivery, avgQuality, avgOverall],
                backgroundColor: ['#3b82f6', '#10b981', '#6366f1']
              }
            ]
          };
          this.hasBreakdownData = true;

          // For trend: Only populate if more than 1 data point or history is available
          this.hasTrendData = false;
        } else {
          this.hasBreakdownData = false;
          this.hasTrendData = false;
        }
        this.cdr.markForCheck();
      },
      error: () => {
        this.hasBreakdownData = false;
        this.hasTrendData = false;
        this.cdr.markForCheck();
      }
    });
  }
}