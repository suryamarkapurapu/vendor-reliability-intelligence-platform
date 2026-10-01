import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatDialog } from '@angular/material/dialog';
import { MatMenuModule } from '@angular/material/menu';

import { ViewMessageDialog } from '../view-message-dialog/view-message-dialog';
import { CommunicationService } from '../../../../services/communication.service';
import { VendorService } from '../../../../services/vendor.service';

interface Message {
  message_id: string;
  vendor: string;
  subject: string;
  type: string;
  date: string;
  status: string;
  attachment: string;
}

@Component({
  selector: 'app-communication-table',
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
  templateUrl: './communication-table.html',
  styleUrl: './communication-table.css'
})
export class CommunicationTable implements OnInit {
  private dialog = inject(MatDialog);
  private communicationService = inject(CommunicationService);
  private vendorService = inject(VendorService);
  private cdr = inject(ChangeDetectorRef);

  displayedColumns = [
    'vendor',
    'subject',
    'type',
    'date',
    'status',
    'actions'
  ];

  dataSource: Message[] = [];
  private vendorsMap: Record<string, string> = {};

  ngOnInit(): void {
    this.vendorService.getVendors().subscribe({
      next: (vendors) => {
        vendors.forEach(v => {
          this.vendorsMap[v.vendor_id] = v.company_name;
        });
        this.loadMessages();
      },
      error: () => this.loadMessages()
    });
  }

  loadMessages(): void {
    this.communicationService.getMessages().subscribe({
      next: (messages) => {
        this.dataSource = messages.map((message) => ({
  message_id: message.message_id,
  vendor: (message.vendor_id
    ? this.vendorsMap[message.vendor_id]
    : null) ?? message.vendor_id ?? 'General',
  subject: message.subject ?? 'No Subject',
  type: 'Message',
  date: message.sent_at,
  status: message.is_read ? 'Read' : 'Unread',
  attachment: '-'
}));
        this.cdr.markForCheck();
      },
      error: () => {
        this.dataSource = [];
        this.cdr.markForCheck();
      }
    });
  }

  viewCommunication(communication: Message): void {

  this.communicationService.markAsRead(
    communication.message_id
  ).subscribe({

    next: () => {

      communication.status = 'Read';

      this.dialog.open(ViewMessageDialog, {
        width: '600px',
        data: communication
      });

      this.loadMessages();
    },

    error: () => {

      this.dialog.open(ViewMessageDialog, {
        width: '600px',
        data: communication
      });

    }

  });

}
}
