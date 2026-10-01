import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';

import { AnalyticsHeader } from './components/analytics-header/analytics-header';
import { AnalyticsSummaryCard } from './components/analytics-summary-card/analytics-summary-card';

import { ProcurementChart } from './components/procurement-chart/procurement-chart';
import { VendorChart } from './components/vendor-chart/vendor-chart';
import { RiskChart } from './components/risk-chart/risk-chart';
import { ContractChart } from './components/contract-chart/contract-chart';
import { AnalyticsService } from '../../services/analytics.service';
import { ContractService } from '../../services/contract.service';
import { VendorPerformanceService } from '../../services/vendor-performance.service';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [
    CommonModule,
    Navbar,
    Sidebar,
    AnalyticsHeader,
    AnalyticsSummaryCard,
    ProcurementChart,
    VendorChart,
    RiskChart,
    ContractChart
  ],
  templateUrl: './analytics.html',
  styleUrl: './analytics.css'
})
export class Analytics implements OnInit {
  totalVendors = '0';
  activeContracts = '0';
  procurementCost = '₹0';
  vendorScore = '0%';

  private analyticsService = inject(AnalyticsService);
  private contractService = inject(ContractService);
  private performanceService = inject(VendorPerformanceService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadMetrics();
  }

  loadMetrics(): void {
    this.analyticsService.getDashboardMetrics().subscribe({
      next: (data) => {
        this.totalVendors = (data.total_vendors ?? 0).toString();
        const spend = Number(data.total_procurement_spend ?? 0);
        this.procurementCost = new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0
        }).format(spend);
        this.cdr.markForCheck();
      },
      error: () => {
        this.totalVendors = '0';
        this.procurementCost = '₹0';
        this.cdr.markForCheck();
      }
    });

    this.contractService.getContracts().subscribe({
      next: (contracts) => {
        const active = contracts.filter(c => String(c.status).toLowerCase() === 'active').length;
        this.activeContracts = active.toString();
        this.cdr.markForCheck();
      },
      error: () => {
        this.activeContracts = '0';
        this.cdr.markForCheck();
      }
    });

    this.performanceService.getRankings().subscribe({
      next: (rankings) => {
        if (rankings && rankings.length > 0) {
          const avg = Math.round(rankings.reduce((sum, r) => sum + Number(r.overall_score || 0), 0) / rankings.length);
          this.vendorScore = `${avg}%`;
        } else {
          this.vendorScore = '0%';
        }
        this.cdr.markForCheck();
      },
      error: () => {
        this.vendorScore = '0%';
        this.cdr.markForCheck();
      }
    });
  }
}