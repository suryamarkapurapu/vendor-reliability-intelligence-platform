import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';

import { PerformanceSummary }
  from './components/performance-summary/performance-summary';

import { PerformanceCharts }
  from './components/performance-charts/performance-charts';

import { VendorRanking }
  from './components/vendor-ranking/vendor-ranking';

import { VendorPerformanceService }
  from '../../services/vendor-performance.service';

import { VendorService }
  from '../../services/vendor.service';

import { AnalyticsService }
  from '../../services/analytics.service';

@Component({
  selector: 'app-vendor-performance',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,

    Navbar,
    Sidebar,
    PerformanceSummary,
    PerformanceCharts,
    VendorRanking
  ],
  templateUrl: './vendor-performance.html',
  styleUrl: './vendor-performance.css'
})
export class VendorPerformance implements OnInit {

  avgReliabilityScore = '0/100';
  onTimeDelivery = '0%';
  avgQualityRating = '0/5';
  highRiskVendors = '0';

  vendors: any[] = [];

  selectedVendorId = '';
  qualityRating = 5;
  deliveryRating = 5;
  communicationRating = 5;
  comments = '';

  ratingMessage = '';
  ratingError = '';

  private performanceService = inject(VendorPerformanceService);
  private vendorService = inject(VendorService);
  private analyticsService = inject(AnalyticsService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadMetrics();
    this.loadVendors();
  }

  loadVendors(): void {
    this.vendorService.getVendors(0, 100).subscribe({
      next: (vendors) => {
        this.vendors = vendors;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Unable to load vendors for rating:', error);
      }
    });
  }

  submitRating(): void {

    this.ratingMessage = '';
    this.ratingError = '';

    if (!this.selectedVendorId) {
      this.ratingError = 'Please select a vendor.';
      return;
    }

   const ratingData = {
  vendor_id: this.selectedVendorId,
  quality_rating: Number(this.qualityRating),
  delivery_rating: Number(this.deliveryRating),
  communication_rating: Number(this.communicationRating),
  comments: this.comments.trim() || undefined
};

    this.performanceService.createRating(ratingData).subscribe({
      next: () => {
        this.ratingMessage = 'Vendor rating submitted successfully.';

        this.selectedVendorId = '';
        this.qualityRating = 5;
        this.deliveryRating = 5;
        this.communicationRating = 5;
        this.comments = '';

        this.loadMetrics();

        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Unable to submit vendor rating:', error);

        this.ratingError =
          error?.error?.detail ||
          'Unable to submit vendor rating.';

        this.cdr.markForCheck();
      }
    });
  }

  loadMetrics(): void {
    this.performanceService.getRankings().subscribe({
      next: (rankings) => {

        if (!rankings || rankings.length === 0) {

          this.avgReliabilityScore = '0/100';
          this.onTimeDelivery = '0%';
          this.avgQualityRating = '0/5';
          this.highRiskVendors = '0';

        } else {

          const totalScore = rankings.reduce(
            (sum, r) => sum + Number(r.overall_score || 0),
            0
          );

          const avgScore =
            (totalScore / rankings.length).toFixed(0);

          this.avgReliabilityScore = `${avgScore}/100`;

          const totalDelivery = rankings.reduce(
            (sum, r) => sum + Number(r.on_time_delivery_rate || 0),
            0
          );

          const avgDelivery =
            (totalDelivery / rankings.length).toFixed(0);

          this.onTimeDelivery = `${avgDelivery}%`;

          const totalQuality = rankings.reduce(
            (sum, r) => sum + Number(r.average_overall_rating || 0),
            0
          );

          const avgQuality =
            (totalQuality / rankings.length).toFixed(1);

          this.avgQualityRating = `${avgQuality}/5`;

          const highRiskCount = rankings.filter(
            r =>
              Number(r.overall_score || 0) < 60 ||
              (r.risk_level || '').toLowerCase() === 'high'
          ).length;

          this.highRiskVendors = highRiskCount.toString();
        }

        this.cdr.markForCheck();
      },

      error: (error) => {
        console.error('Unable to load vendor performance:', error);

        this.avgReliabilityScore = '0/100';
        this.onTimeDelivery = '0%';
        this.avgQualityRating = '0/5';
        this.highRiskVendors = '0';

        this.cdr.markForCheck();
      }
    });
  }
}