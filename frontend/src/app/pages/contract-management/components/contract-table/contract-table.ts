import { Component, EventEmitter, OnInit, Output, ChangeDetectorRef } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';

import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { ViewContractDialog } from '../view-contract-dialog/view-contract-dialog';
import { ContractService } from '../../../../services/contract.service';
import { VendorService } from '../../../../services/vendor.service';

export interface Contract {
  contractId: string;
  vendor: string;
  startDate: string;
  endDate: string;
  contractValue: number;
  status: string;
}

@Component({
  selector: 'app-contract-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatPaginatorModule,
    MatChipsModule,
    DecimalPipe
  ],
  templateUrl: './contract-table.html',
  styleUrl: './contract-table.css'
})
export class ContractTable implements OnInit {
  @Output() contractDataChanged = new EventEmitter<void>();

  displayedColumns = [
    'contractId',
    'vendor',
    'startDate',
    'endDate',
    'contractValue',
    'status',
    'actions'
  ];

  dataSource: Contract[] = [];
  private vendorsMap: Record<string, string> = {};

  constructor(
    private dialog: MatDialog,
    private contractService: ContractService,
    private vendorService: VendorService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.vendorService.getVendors().subscribe({
      next: (vendors) => {
        vendors.forEach(v => {
          this.vendorsMap[v.vendor_id] = v.company_name;
        });
        this.loadContracts();
      },
      error: () => this.loadContracts()
    });
  }

  loadContracts(): void {
    this.contractService.getContracts().subscribe({
      next: (contracts) => {
        this.dataSource = contracts.map((contract) => ({
          contractId: contract.contract_number,
          vendor: this.vendorsMap[contract.vendor_id] ?? contract.vendor_id,
          startDate: contract.start_date,
          endDate: contract.end_date,
          contractValue: Number(contract.contract_value ?? 0),
          status: contract.status
        }));
        this.cdr.markForCheck();
        this.contractDataChanged.emit();
      },
      error: () => {
        this.dataSource = [];
        this.cdr.markForCheck();
      }
    });
  }

  view(contract: Contract): void {
    this.dialog.open(ViewContractDialog, {
      width: '600px',
      data: contract
    });
  }
}
