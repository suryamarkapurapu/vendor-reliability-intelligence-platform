import { Component, EventEmitter, OnInit, Output, ChangeDetectorRef } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialog } from '@angular/material/dialog';
import { ViewProcurementDialog } from '../view-procurement-dialog/view-procurement-dialog';
import { EditProcurementDialog } from '../edit-procurement-dialog/edit-procurement-dialog';
import { ProcurementService } from '../../../../services/procurement.service';

export interface Procurement {
  id?: string;
  requestId: string;
  item: string;
  vendor: string;
  quantity: number;
  budget: number;
  requiredDate: string;
  status: string;
  priority: string;
}

@Component({
  selector: 'app-procurement-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatChipsModule,
    MatPaginatorModule,
    DecimalPipe,
    MatMenuModule
  ],
  templateUrl: './procurement-table.html',
  styleUrl: './procurement-table.css'
})
export class ProcurementTable implements OnInit {
  @Output() procurementDataChanged = new EventEmitter<void>();

  displayedColumns: string[] = [
    'requestId',
    'item',
    'quantity',
    'budget',
    'requiredDate',
    'priority',
    'status',
    'actions'
  ];

  dataSource: Procurement[] = [];

  constructor(
    private dialog: MatDialog,
    private procurementService: ProcurementService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadRequests();
  }

  loadRequests(): void {
    this.procurementService.getRequests().subscribe({
      next: (requests) => {
        this.dataSource = requests.map((request) => ({
          id: request.request_id,
          requestId: request.request_number,
          item: request.item_description,
          vendor: '-',
          quantity: Number(request.quantity),
          budget: Number(request.estimated_cost ?? 0),
          requiredDate: request.required_by_date ?? '-',
          status: request.status,
          priority: request.priority
        }));
        this.cdr.markForCheck();
        this.procurementDataChanged.emit();
      },
      error: () => {
        this.dataSource = [];
        this.cdr.markForCheck();
      }
    });
  }

  viewProcurement(procurement: Procurement): void {
    this.dialog.open(ViewProcurementDialog, {
      width: '600px',
      data: procurement
    });
  }

  editProcurement(procurement: Procurement): void {
    const dialogRef = this.dialog.open(EditProcurementDialog, {
      width: '550px',
      data: { ...procurement }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && (result.id || procurement.id)) {
        const targetId = result.id || procurement.id;
        const payload = {
          item_description: result.item,
          quantity: Number(result.quantity),
          estimated_cost: Number(result.budget),
          priority: String(result.priority || 'MEDIUM').toUpperCase()
        };

        this.procurementService.updateRequest(targetId, payload).subscribe({
          next: () => this.loadRequests(),
          error: (err) => console.error('Error persisting procurement request update:', err)
        });
      }
    });
  }

  approveProcurement(procurement: Procurement): void {
    if (procurement.id) {
      this.procurementService.approveRequest(procurement.id).subscribe({
        next: () => this.loadRequests(),
        error: (err) => console.error('Error approving procurement request:', err)
      });
    }
  }

  rejectProcurement(procurement: Procurement): void {
    if (procurement.id) {
      this.procurementService.rejectRequest(procurement.id).subscribe({
        next: () => this.loadRequests(),
        error: (err) => console.error('Error rejecting procurement request:', err)
      });
    }
  }

  cancelProcurement(procurement: Procurement): void {
    if (procurement.id) {
      this.procurementService.cancelRequest(procurement.id).subscribe({
        next: () => this.loadRequests(),
        error: (err) => console.error('Error cancelling procurement request:', err)
      });
    }
  }
}
