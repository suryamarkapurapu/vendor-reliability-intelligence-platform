import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { VendorService } from '../../../../services/vendor.service';

@Component({
  selector: 'app-purchase-toolbar',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule
  ],
  templateUrl: './purchase-toolbar.html',
  styleUrl: './purchase-toolbar.css'
})
export class PurchaseToolbar implements OnInit {
  private vendorService = inject(VendorService);
  private cdr = inject(ChangeDetectorRef);

  searchText = '';
  status = '';
  supplier = '';
  vendors: any[] = [];

  ngOnInit(): void {
    this.vendorService.getVendors().subscribe({
      next: (vendors) => {
        this.vendors = vendors;
        this.cdr.markForCheck();
      },
      error: () => {
        this.vendors = [];
        this.cdr.markForCheck();
      }
    });
  }
}