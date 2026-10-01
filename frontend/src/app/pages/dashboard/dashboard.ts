import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';

import { DashboardHeader } from './components/dashboard-header/dashboard-header';
import { KpiCard } from './components/kpi-card/kpi-card';
import { ChartCard } from './components/chart-card/chart-card';
import { RecentOrders } from './components/recent-orders/recent-orders';
import { RiskAlerts } from './components/risk-alerts/risk-alerts';
import { RecentActivity } from './components/recent-activity/recent-activity';

import { MatExpansionModule } from '@angular/material/expansion';

import { ChartConfiguration } from 'chart.js';
import { AnalyticsService } from '../../services/analytics.service';


@Component({
  selector: 'app-dashboard',

  standalone: true,

  imports: [
    Navbar,
    Sidebar,
    DashboardHeader,
    KpiCard,
    ChartCard,
    RecentOrders,
    RiskAlerts,
    RecentActivity,
    MatExpansionModule
  ],

  templateUrl: './dashboard.html',

  styleUrl: './dashboard.css'
})

export class Dashboard implements OnInit {

  totalVendors = 0;
  totalPurchaseOrders = 0;
  totalProcurementSpend = 0;
  totalOpenIssues = 0;

  vendorPerformanceData: ChartConfiguration['data'] = {
    labels: [],
    datasets: [{ label: 'Vendor Spend', data: [] }]
  };

  procurementAnalyticsData: ChartConfiguration['data'] = {
    labels: [],
    datasets: [{ label: 'Procurement Spend', data: [], tension: 0.4, fill: false }]
  };

  constructor(
    private analyticsService: AnalyticsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.analyticsService.getDashboardMetrics().subscribe({
      next: (metrics) => {
        this.totalVendors = metrics.total_vendors ?? 0;
        this.totalPurchaseOrders = metrics.total_purchase_orders ?? 0;
        this.totalProcurementSpend = metrics.total_procurement_spend ?? 0;
        this.totalOpenIssues = metrics.total_open_issues ?? 0;
        this.cdr.markForCheck();
      },
      error: () => {
        this.cdr.markForCheck();
      }
    });

    this.analyticsService.getVendorAnalytics().subscribe({
      next: (data) => {
        const vendors = data.top_vendors_by_spend ?? [];

        this.vendorPerformanceData = {
          labels: vendors.map((vendor: any) => vendor.vendor_name),
          datasets: [
            {
              label: 'Vendor Spend',
              data: vendors.map((vendor: any) => Number(vendor.total_spend ?? 0))
            }
          ]
        };
        this.cdr.markForCheck();
      },
      error: () => {
        this.cdr.markForCheck();
      }
    });

    this.analyticsService.getProcurementAnalytics().subscribe({
      next: (data) => {
        const trend = data.monthly_spend_trend ?? [];

        this.procurementAnalyticsData = {
          labels: trend.map((point: any) => point.month),
          datasets: [
            {
              label: 'Procurement Spend',
              data: trend.map((point: any) => Number(point.total_amount ?? 0)),
              tension: 0.4,
              fill: false
            }
          ]
        };
        this.cdr.markForCheck();
      },
      error: () => {
        this.cdr.markForCheck();
      }
    });
  }

}
