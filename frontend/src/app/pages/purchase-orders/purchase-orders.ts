import { Component, OnInit, ViewChild, inject, ChangeDetectorRef } from '@angular/core';
import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';
import { PurchaseHeader } from './components/purchase-header/purchase-header';
import { PurchaseSummaryCard } from './components/purchase-summary-card/purchase-summary-card';
import { PurchaseToolbar } from './components/purchase-toolbar/purchase-toolbar';
import { PurchaseTable } from './components/purchase-table/purchase-table';
import { PurchaseOrderService } from '../../services/purchase-order.service';
import { DeliveryTracking } from './components/delivery-tracking/delivery-tracking';

@Component({
  selector: 'app-purchase-orders',
  standalone: true,
  imports: [
    Navbar,
    Sidebar,
    PurchaseHeader,
    PurchaseSummaryCard,
    PurchaseToolbar,
    PurchaseTable,
    DeliveryTracking
  ],
  templateUrl: './purchase-orders.html',
  styleUrl: './purchase-orders.css'
})
export class PurchaseOrders implements OnInit {
  @ViewChild(PurchaseTable) purchaseTable?: PurchaseTable;

  totalOrders = 0;
  approvedOrders = 0;
  pendingOrders = 0;
  completedOrders = 0;

  private purchaseOrderService = inject(PurchaseOrderService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadSummaryMetrics();
  }

  loadSummaryMetrics(): void {
    this.purchaseOrderService.getPurchaseOrders().subscribe({
      next: (orders) => {
        this.totalOrders = orders.length;
        this.approvedOrders = orders.filter(o => String(o.status).toUpperCase() === 'APPROVED').length;
        this.pendingOrders = orders.filter(o => String(o.status).toUpperCase() === 'PENDING').length;
        this.completedOrders = orders.filter(o => {
          const st = String(o.status).toUpperCase();
          return st === 'COMPLETED' || st === 'DELIVERED';
        }).length;
        this.cdr.markForCheck();
      },
      error: () => {
        this.totalOrders = 0;
        this.approvedOrders = 0;
        this.pendingOrders = 0;
        this.completedOrders = 0;
        this.cdr.markForCheck();
      }
    });
  }

  onPoCreated(): void {
    this.loadSummaryMetrics();
    if (this.purchaseTable) {
      this.purchaseTable.loadPurchaseOrders();
    }
  }

  onPoDataChanged(): void {
    this.loadSummaryMetrics();
  }
}