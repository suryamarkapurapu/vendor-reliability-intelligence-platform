import { Component, EventEmitter, Output, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import { AddContractDialog } from '../add-contract-dialog/add-contract-dialog';
import { ContractService } from '../../../../services/contract.service';

@Component({
  selector: 'app-contract-header',
  standalone: true,
  imports: [
    MatButtonModule,
    MatDialogModule
  ],
  templateUrl: './contract-header.html',
  styleUrl: './contract-header.css'
})
export class ContractHeader {

  @Output() contractCreated = new EventEmitter<void>();

  private dialog = inject(MatDialog);
  private contractService = inject(ContractService);

  newContract() {
    const dialogRef = this.dialog.open(AddContractDialog, {
      width: '700px',
      maxHeight: '90vh',
      autoFocus: false
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && (result.vendor || result.vendor_id)) {
        const payload = {
          contract_number: result.contractId || ('CNT-' + Math.floor(1000 + Math.random() * 9000)),
          vendor_id: result.vendor || result.vendor_id,
          contract_type: result.contractType || 'Standard Agreement',
          start_date: result.startDate,
          end_date: result.endDate,
          contract_value: Number(result.contractValue || 0),
          status: String(result.status || 'active').toLowerCase()
        };

        this.contractService.createContract(payload).subscribe({
          next: () => {
            this.contractCreated.emit();
          },
          error: (err) => {
            console.error('Error creating contract:', err);
          }
        });
      }
    });
  }
}