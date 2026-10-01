import { Component, EventEmitter, Output, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import { AddPurchaseOrderDialog } from '../add-purchase-order-dialog/add-purchase-order-dialog';
import { PurchaseOrderService } from '../../../../services/purchase-order.service';

@Component({
  selector: 'app-purchase-header',
  standalone: true,
  imports: [
    MatButtonModule,
    MatDialogModule
  ],
  templateUrl: './purchase-header.html',
  styleUrl: './purchase-header.css'
})
export class PurchaseHeader {

  @Output() poCreated = new EventEmitter<void>();

  private dialog = inject(MatDialog);
  private purchaseOrderService = inject(PurchaseOrderService);

  newPurchaseOrder() {
  const dialogRef = this.dialog.open(AddPurchaseOrderDialog, {
    width: '700px',
    maxHeight: '90vh',
    autoFocus: false
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result && (result.supplier || result.vendor_id)) {

      const payload = {
        vendor_id: result.supplier || result.vendor_id,

        expected_delivery_date:
          result.deliveryDate || undefined,

        items: [
          {
            item_name: result.item || 'General Order Item',
            quantity: Number(result.quantity || 1),
            unit_price: Number(result.unitPrice || 0)
          }
        ]
      };

      console.log('Creating Purchase Order:', payload);

      this.purchaseOrderService.createPurchaseOrder(payload).subscribe({
        next: (response) => {
          console.log('Purchase Order created:', response);
          this.poCreated.emit();
        },
        error: (err) => {
          console.error('Error creating purchase order:', err);
        }
      });
    }
  });
}
}