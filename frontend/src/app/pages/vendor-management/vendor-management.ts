import { Component, OnInit, ViewChild, inject, ChangeDetectorRef } from '@angular/core';
import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';
import { VendorHeader } from './components/vendor-header/vendor-header';
import { VendorToolbar } from './components/vendor-toolbar/vendor-toolbar';
import { VendorTable } from './components/vendor-table/vendor-table';
import { VendorSummaryCard } from './components/vendor-summary-card/vendor-summary-card';
import { AnalyticsService } from '../../services/analytics.service';
import { VendorService } from '../../services/vendor.service';

@Component({
  selector: 'app-vendor-management',
  standalone: true,
  imports: [
    Navbar,
    Sidebar,
    VendorHeader,
    VendorToolbar,
    VendorTable,
    VendorSummaryCard,
  ],
  templateUrl: './vendor-management.html',
  styleUrl: './vendor-management.css'
})
export class VendorManagement implements OnInit {
  @ViewChild(VendorTable) vendorTable?: VendorTable;

  searchQuery = '';
  categoryFilter = 'All';
  statusFilter = 'All';

  totalVendors = 0;
  activeVendors = 0;
  pendingApproval = 0;
  inactiveVendors = 0;

  private analyticsService = inject(AnalyticsService);
  private vendorService = inject(VendorService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadSummaryMetrics();
  }

  loadSummaryMetrics(): void {
    this.analyticsService.getVendorAnalytics().subscribe({
      next: (data) => {
        this.totalVendors = data.total_vendors ?? 0;
        const statusMap = data.vendors_by_status ?? {};
        this.activeVendors = statusMap['approved'] ?? data.active_vendors ?? 0;
        this.pendingApproval = statusMap['pending'] ?? 0;
        this.inactiveVendors = (statusMap['suspended'] ?? 0) + (statusMap['blacklisted'] ?? 0) + (statusMap['rejected'] ?? 0);
        this.cdr.markForCheck();
      },
      error: () => {
        this.totalVendors = 0;
        this.activeVendors = 0;
        this.pendingApproval = 0;
        this.inactiveVendors = 0;
        this.cdr.markForCheck();
      }
    });
  }

  onVendorCreated(): void {
    this.loadSummaryMetrics();
    if (this.vendorTable) {
      this.vendorTable.loadVendors();
    }
    this.cdr.markForCheck();
  }

  onVendorDataChanged(): void {
    this.loadSummaryMetrics();
    this.cdr.markForCheck();
  }

  onSearchChange(query: string): void {
    this.searchQuery = query;
  }

  onCategoryChange(cat: string): void {
    this.categoryFilter = cat;
  }

  onStatusChange(stat: string): void {
    this.statusFilter = stat;
  }
}