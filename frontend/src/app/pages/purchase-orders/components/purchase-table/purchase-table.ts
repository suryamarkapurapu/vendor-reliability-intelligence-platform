import { Component, EventEmitter, OnInit, Output, ChangeDetectorRef } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';

import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialog } from '@angular/material/dialog';
import { ViewPurchaseOrderDialog } from '../view-purchase-order-dialog/view-purchase-order-dialog';
import { PurchaseOrderService } from '../../../../services/purchase-order.service';

export interface PurchaseOrder {
  id?: string;
  poNumber: string;
  supplier: string;
  item: string;
  quantity: number;
  totalAmount: number;
  orderDate: string;
  deliveryDate: string;
  status: string;
}

@Component({
  selector: 'app-purchase-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatPaginatorModule,
    MatChipsModule,
    MatMenuModule,
    DecimalPipe
  ],
  templateUrl: './purchase-table.html',
  styleUrl: './purchase-table.css'
})
export class PurchaseTable implements OnInit {
  @Output() poDataChanged = new EventEmitter<void>();

  displayedColumns = [
    'poNumber',
    'supplier',
    'item',
    'quantity',
    'totalAmount',
    'orderDate',
    'deliveryDate',
    'status',
    'actions'
  ];

  dataSource: PurchaseOrder[] = [];

  constructor(
    private dialog: MatDialog,
    private purchaseOrderService: PurchaseOrderService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadPurchaseOrders();
  }

  loadPurchaseOrders(): void {
    this.purchaseOrderService.getPurchaseOrders().subscribe({
      next: (orders) => {
        this.dataSource = orders.map((order) => ({
          id: order.po_id,
          poNumber: order.po_number,
          supplier: order.vendor_name ?? order.vendor_id,
          item: order.items?.[0]?.item_name ?? 'Item Order',
          quantity: Number(order.items?.[0]?.quantity ?? 1),
          totalAmount: Number(order.total_amount ?? 0),
          orderDate: order.order_date,
          deliveryDate: order.expected_delivery_date ?? '-',
          status: order.status
        }));
        this.cdr.markForCheck();
        this.poDataChanged.emit();
      },
      error: () => {
        this.dataSource = [];
        this.cdr.markForCheck();
      }
    });
  }

  view(order: PurchaseOrder): void {
    this.dialog.open(ViewPurchaseOrderDialog, {
      width: '600px',
      data: order
    });
  }

  approveOrder(order: PurchaseOrder): void {
    if (order.id) {
      this.purchaseOrderService.approvePurchaseOrder(order.id).subscribe({
        next: () => this.loadPurchaseOrders(),
        error: (err) => console.error('Error approving PO:', err)
      });
    }
  }

  deliverOrder(order: PurchaseOrder): void {
    if (order.id) {
      this.purchaseOrderService.deliverPurchaseOrder(order.id).subscribe({
        next: () => this.loadPurchaseOrders(),
        error: (err) => console.error('Error marking PO delivered:', err)
      });
    }
  }

  completeOrder(order: PurchaseOrder): void {
    if (order.id) {
      this.purchaseOrderService.completePurchaseOrder(order.id).subscribe({
        next: () => this.loadPurchaseOrders(),
        error: (err) => console.error('Error completing PO:', err)
      });
    }
  }
}
