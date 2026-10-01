import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { PurchaseOrderService } from '../../../../services/purchase-order.service';

interface PurchaseOrder {
  poId: string;
  vendor: string;
  amount: string;
  status: string;
}

@Component({
  selector: 'app-recent-orders',
  standalone: true,
  imports: [MatTableModule, MatCardModule],
  templateUrl: './recent-orders.html',
  styleUrl: './recent-orders.css'
})
export class RecentOrders implements OnInit {
  displayedColumns: string[] = [
    'poId',
    'vendor',
    'amount',
    'status'
  ];

  dataSource: PurchaseOrder[] = [];

  constructor(
    private purchaseOrderService: PurchaseOrderService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.purchaseOrderService.getPurchaseOrders().subscribe({
      next: (orders) => {
        this.dataSource = orders.slice(0, 5).map((order) => ({
          poId: order.po_number,
          vendor: order.vendor_name ?? order.vendor_id,
          amount: this.formatAmount(Number(order.total_amount ?? 0)),
          status: order.status
        }));
        this.cdr.markForCheck();
      },
      error: () => {
        this.dataSource = [];
        this.cdr.markForCheck();
      }
    });
  }

  private formatAmount(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  }
}
