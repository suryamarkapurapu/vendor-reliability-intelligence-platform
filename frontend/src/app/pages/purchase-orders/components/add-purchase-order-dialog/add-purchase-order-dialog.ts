import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { VendorService } from '../../../../services/vendor.service';

@Component({
  selector: 'app-add-purchase-order-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule
  ],
  templateUrl: './add-purchase-order-dialog.html',
  styleUrl: './add-purchase-order-dialog.css'
})
export class AddPurchaseOrderDialog implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<AddPurchaseOrderDialog>);
  private vendorService = inject(VendorService);
  private cdr = inject(ChangeDetectorRef);

  vendors: any[] = [];
  isLoadingVendors = false;

  purchaseForm = this.fb.group({
    poNumber: ['PO-' + Math.floor(1000 + Math.random() * 9000), Validators.required],
    supplier: ['', Validators.required],
    item: ['', Validators.required],
    quantity: [1, [Validators.required, Validators.min(1)]],
    unitPrice: [0, [Validators.required, Validators.min(0)]],
    totalAmount: [0, Validators.required],
    orderDate: [new Date().toISOString().substring(0, 10), Validators.required],
    deliveryDate: ['', Validators.required],
    status: ['pending', Validators.required],
    remarks: ['']
  });

  ngOnInit(): void {
    this.isLoadingVendors = true;
    this.vendorService.getVendors().subscribe({
      next: (data) => {
        // Purchase orders require approved vendors according to backend rules
        this.vendors = data.filter(v => v.status === 'approved');
        // If no approved vendors, show all so user can see why
        if (this.vendors.length === 0 && data.length > 0) {
          this.vendors = data;
        }
        if (this.vendors.length > 0) {
          this.purchaseForm.patchValue({ supplier: this.vendors[0].vendor_id });
        }
        this.isLoadingVendors = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.vendors = [];
        this.isLoadingVendors = false;
        this.cdr.markForCheck();
      }
    });

    this.purchaseForm.get('quantity')?.valueChanges.subscribe(() => this.updateTotal());
    this.purchaseForm.get('unitPrice')?.valueChanges.subscribe(() => this.updateTotal());
  }

  private updateTotal(): void {
    const qty = Number(this.purchaseForm.get('quantity')?.value || 0);
    const price = Number(this.purchaseForm.get('unitPrice')?.value || 0);
    this.purchaseForm.patchValue({ totalAmount: qty * price }, { emitEvent: false });
  }

  save() {
    if (this.purchaseForm.invalid) {
      this.purchaseForm.markAllAsTouched();
      return;
    }
    this.dialogRef.close(this.purchaseForm.value);
  }

  cancel() {
    this.dialogRef.close();
  }
}