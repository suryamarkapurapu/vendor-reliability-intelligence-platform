import { Component, OnInit, ViewChild, inject, ChangeDetectorRef } from '@angular/core';

import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';
import { ContractHeader } from './components/contract-header/contract-header';
import { ContractSummaryCard } from './components/contract-summary-card/contract-summary-card';
import { ContractToolbar } from './components/contract-toolbar/contract-toolbar';
import { ContractTable } from './components/contract-table/contract-table';
import { ContractService } from '../../services/contract.service';

@Component({
  selector: 'app-contract-management',
  standalone: true,
  imports: [
    Navbar,
    Sidebar,
    ContractHeader,
    ContractSummaryCard,
    ContractToolbar,
    ContractTable
  ],
  templateUrl: './contract-management.html',
  styleUrl: './contract-management.css'
})
export class ContractManagement implements OnInit {
  @ViewChild(ContractTable) contractTable?: ContractTable;

  totalContracts = 0;
  activeContracts = 0;
  expiringContracts = 0;
  expiredContracts = 0;

  private contractService = inject(ContractService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadSummaryMetrics();
  }

  loadSummaryMetrics(): void {
    this.contractService.getContracts().subscribe({
      next: (contracts) => {
        this.totalContracts = contracts.length;
        this.activeContracts = contracts.filter(c => String(c.status).toLowerCase() === 'active').length;
        this.expiringContracts = contracts.filter(c => String(c.status).toLowerCase() === 'expiring' || String(c.status).toLowerCase() === 'draft').length;
        this.expiredContracts = contracts.filter(c => String(c.status).toLowerCase() === 'expired' || String(c.status).toLowerCase() === 'terminated').length;
        this.cdr.markForCheck();
      },
      error: () => {
        this.totalContracts = 0;
        this.activeContracts = 0;
        this.expiringContracts = 0;
        this.expiredContracts = 0;
        this.cdr.markForCheck();
      }
    });
  }

  onContractCreated(): void {
    this.loadSummaryMetrics();
    if (this.contractTable) {
      this.contractTable.loadContracts();
    }
  }

  onContractDataChanged(): void {
    this.loadSummaryMetrics();
  }
}