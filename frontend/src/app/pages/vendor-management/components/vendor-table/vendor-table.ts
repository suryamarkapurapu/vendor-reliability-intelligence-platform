import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatPaginatorModule } from '@angular/material/paginator';
import { ViewVendorDialog } from '../view-vendor-dialog/view-vendor-dialog';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialog } from '@angular/material/dialog';
import { EditVendorDialog } from '../edit-vendor-dialog/edit-vendor-dialog';
import { DeleteVendorDialog } from '../delete-vendor-dialog/delete-vendor-dialog';
import { VendorService } from '../../../../services/vendor.service';

export interface Vendor {
  id: string;
  vendorCode: string;
  name: string;
  category: string;
  categoryId: number;
  vendorType: string;
  contact: string;
  email: string;
  status: string;
  rating: number;
  risk: string;
}

@Component({
  selector: 'app-vendor-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatPaginatorModule,
    MatMenuModule
  ],
  templateUrl: './vendor-table.html',
  styleUrl: './vendor-table.css'
})
export class VendorTable implements OnInit, OnChanges {
  @Input() searchQuery = '';
  @Input() categoryFilter = 'All';
  @Input() statusFilter = 'All';

  @Output() vendorDataChanged = new EventEmitter<void>();

  displayedColumns: string[] = [
    'name',
    'category',
    'vendorType',
    'contact',
    'email',
    'status',
    'actions'
  ];

  allVendors: Vendor[] = [];
  dataSource: Vendor[] = [];

  private dialog = inject(MatDialog);
  private vendorService = inject(VendorService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadVendors();
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.applyFilters();
  }

  public loadVendors(): void {
    this.vendorService.getVendors().subscribe({
      next: (vendors) => {
        this.allVendors = vendors.map((vendor) => this.mapVendor(vendor));
        this.applyFilters();
        this.vendorDataChanged.emit();
      },
      error: () => {
        this.allVendors = [];
        this.dataSource = [];
        this.cdr.markForCheck();
      }
    });
  }

  private applyFilters(): void {
    let filtered = [...this.allVendors];

    if (this.searchQuery && this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase().trim();
      filtered = filtered.filter(v =>
        v.name.toLowerCase().includes(q) ||
        v.vendorCode.toLowerCase().includes(q) ||
        v.category.toLowerCase().includes(q)
      );
    }

    if (this.categoryFilter && this.categoryFilter !== 'All') {
      filtered = filtered.filter(v => v.category.toLowerCase() === this.categoryFilter.toLowerCase());
    }

    if (this.statusFilter && this.statusFilter !== 'All') {
      filtered = filtered.filter(v => v.status.toLowerCase() === this.statusFilter.toLowerCase());
    }

    this.dataSource = filtered;
    this.cdr.markForCheck();
  }

  private mapVendor(vendor: any): Vendor {
    return {
      id: vendor.vendor_id,
      vendorCode: vendor.vendor_code,
      name: vendor.company_name,
      category: vendor.category_name ?? (vendor.category?.category_name ?? `Category ${vendor.category_id}`),
      categoryId: vendor.category_id,
      vendorType: vendor.website ?? '-',
      contact: vendor.tax_id ?? '-',
      email: vendor.address_line ?? '-',
      status: vendor.status,
      rating: 0,
      risk: '-'
    };
  }

  viewVendor(vendor: Vendor): void {
    this.dialog.open(ViewVendorDialog, {
      width: '550px',
      data: vendor
    });
  }

  editVendor(vendor: Vendor): void {
    const dialogRef = this.dialog.open(EditVendorDialog, {
      width: '500px',
      data: { ...vendor }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        const updateData = {
          vendor_code: vendor.vendorCode,
          company_name: result.name,
          category_id: result.categoryId ?? vendor.categoryId
        };

        this.vendorService.updateVendor(vendor.id, updateData).subscribe({
          next: () => this.loadVendors()
        });
      }
    });
  }

  approveVendor(vendor: Vendor): void {
    this.vendorService.approveVendor(vendor.id).subscribe({
      next: () => this.loadVendors(),
      error: (err) => console.error('Error approving vendor:', err)
    });
  }

  deleteVendor(vendor: Vendor): void {
    const dialogRef = this.dialog.open(DeleteVendorDialog, {
      width: '420px',
      data: vendor
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.vendorService.deleteVendor(vendor.id).subscribe({
          next: () => {
            this.loadVendors();
            this.vendorDataChanged.emit();
          },
          error: (err) => console.error('Error deleting vendor:', err)
        });
      }
    });
  }
}
