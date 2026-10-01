import { Component, EventEmitter, Output, inject } from '@angular/core';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { AddVendorDialog } from '../add-vendor-dialog/add-vendor-dialog';
import { VendorService } from '../../../../services/vendor.service';

@Component({
  selector: 'app-vendor-header',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule],
  templateUrl: './vendor-header.html',
  styleUrl: './vendor-header.css'
})
export class VendorHeader {

  @Output() vendorCreated = new EventEmitter<void>();

  private dialog = inject(MatDialog);
  private vendorService = inject(VendorService);

  openDialog() {
    const dialogRef = this.dialog.open(AddVendorDialog, {
      width: '600px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && (result.vendorName || result.name)) {
        const categoryIdMap: Record<string, number> = {
          'Raw Material Suppliers': 1,
          'Equipment Vendors': 2,
          'IT Vendors': 3,
          'Service Providers': 4,
          'Logistics Partners': 5,
          'Maintenance Vendors': 6
        };
        const catId = typeof result.category === 'number' ? result.category : (categoryIdMap[result.category] || Number(result.category) || 1);
        const code = 'VEND-' + Math.floor(1000 + Math.random() * 9000);

        const payload = {
          vendor_code: code,
          company_name: result.vendorName || result.name,
          category_id: catId,
          tax_id: result.contact || undefined,
          website: result.vendorType || undefined,
          address_line: result.address || undefined
        };

        this.vendorService.createVendor(payload).subscribe({
          next: (created) => {
            if (result.status === 'approved' && created?.vendor_id) {
              this.vendorService.approveVendor(created.vendor_id).subscribe({
                next: () => this.vendorCreated.emit(),
                error: () => this.vendorCreated.emit()
              });
            } else {
              this.vendorCreated.emit();
            }
          },
          error: (err) => {
            console.error('Error creating vendor:', err);
          }
        });
      }
    });
  }
}
