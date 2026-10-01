import { Component, OnInit, ViewChild, inject, ChangeDetectorRef } from '@angular/core';
import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';
import { ProcurementHeader } from './components/procurement-header/procurement-header';
import { ProcurementSummaryCard } from './components/procurement-summary-card/procurement-summary-card';
import { ProcurementToolbar } from './components/procurement-toolbar/procurement-toolbar';
import { ProcurementTable } from './components/procurement-table/procurement-table';
import { ProcurementService } from '../../services/procurement.service';

@Component({
  selector: 'app-procurement-management',
  standalone: true,
  imports: [
    Navbar,
    Sidebar,
    ProcurementHeader,
    ProcurementSummaryCard,
    ProcurementToolbar,
    ProcurementTable
  ],
  templateUrl: './procurement-management.html',
  styleUrl: './procurement-management.css'
})
export class ProcurementManagement implements OnInit {
  @ViewChild(ProcurementTable) procurementTable?: ProcurementTable;

  totalRequests = 0;
  approvedRequests = 0;
  pendingRequests = 0;
  totalSpend = '₹0';

  private procurementService = inject(ProcurementService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadSummaryMetrics();
  }

  loadSummaryMetrics(): void {
    this.procurementService.getRequests().subscribe({
      next: (requests) => {
        this.totalRequests = requests.length;
        this.approvedRequests = requests.filter(r => String(r.status).toUpperCase() === 'APPROVED').length;
        this.pendingRequests = requests.filter(r => String(r.status).toUpperCase() === 'PENDING').length;
        const total = requests.reduce((sum, r) => sum + Number(r.estimated_cost ?? 0), 0);
        this.totalSpend = new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0
        }).format(total);
        this.cdr.markForCheck();
      },
      error: () => {
        this.totalRequests = 0;
        this.approvedRequests = 0;
        this.pendingRequests = 0;
        this.totalSpend = '₹0';
        this.cdr.markForCheck();
      }
    });
  }

  onRequestCreated(): void {
    this.loadSummaryMetrics();
    if (this.procurementTable) {
      this.procurementTable.loadRequests();
    }
  }

  onProcurementDataChanged(): void {
    this.loadSummaryMetrics();
  }
}