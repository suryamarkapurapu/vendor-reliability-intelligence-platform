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
  selector: 'app-add-contract-dialog',
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
  templateUrl: './add-contract-dialog.html',
  styleUrl: './add-contract-dialog.css'
})
export class AddContractDialog implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<AddContractDialog>);
  private vendorService = inject(VendorService);
  private cdr = inject(ChangeDetectorRef);

  vendors: any[] = [];
  isLoadingVendors = false;

  contractForm = this.fb.group({
    contractId: ['CNT-' + Math.floor(1000 + Math.random() * 9000), Validators.required],
    vendor: ['', Validators.required],
    contractType: ['Standard Agreement'],
    startDate: [new Date().toISOString().substring(0, 10), Validators.required],
    endDate: ['', Validators.required],
    contractValue: [0, [Validators.required, Validators.min(0)]],
    status: ['active', Validators.required],
    description: ['']
  });

  ngOnInit(): void {
    this.isLoadingVendors = true;
    this.vendorService.getVendors().subscribe({
      next: (data) => {
        this.vendors = data;
        if (this.vendors.length > 0) {
          this.contractForm.patchValue({ vendor: this.vendors[0].vendor_id });
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
  }

  save() {
    if (this.contractForm.invalid) {
      this.contractForm.markAllAsTouched();
      return;
    }
    this.dialogRef.close(this.contractForm.value);
  }

  cancel() {
    this.dialogRef.close();
  }
}