import { Component, EventEmitter, Output, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import { AddProcurementDialog } from '../add-procurement-dialog/add-procurement-dialog';
import { ProcurementService } from '../../../../services/procurement.service';

@Component({
  selector: 'app-procurement-header',
  standalone: true,
  imports: [
    MatButtonModule,
    MatDialogModule
  ],
  templateUrl: './procurement-header.html',
  styleUrl: './procurement-header.css'
})
export class ProcurementHeader {

  @Output() requestCreated = new EventEmitter<void>();

  private dialog = inject(MatDialog);
  private procurementService = inject(ProcurementService);

  newProcurement(){
    const dialogRef = this.dialog.open(AddProcurementDialog, {
      width: '700px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && result.item) {
        const payload = {
          item_description: result.item,
          quantity: Number(result.quantity || 1),
          estimated_cost: Number(result.budget || 0),
          priority: String(result.priority || 'medium').toLowerCase(),
          required_by_date: result.requiredDate || undefined
        };

        this.procurementService.createRequest(payload).subscribe({
          next: () => {
            this.requestCreated.emit();
          },
          error: (err) => {
            console.error('Error creating procurement request:', err);
          }
        });
      }
    });
  }
}