import { Component, OnInit, ViewChild, inject, ChangeDetectorRef } from '@angular/core';
import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';
import { CommunicationHeader } from './components/communication-header/communication-header';
import { CommunicationSummaryCard } from './components/communication-summary-card/communication-summary-card';
import { CommunicationToolbar } from './components/communication-toolbar/communication-toolbar';
import { CommunicationTable } from './components/communication-table/communication-table';
import { CommunicationService } from '../../services/communication.service';

@Component({
  selector: 'app-communication',
  standalone: true,
  imports: [
    Navbar,
    Sidebar,
    CommunicationHeader,
    CommunicationSummaryCard,
    CommunicationToolbar,
    CommunicationTable
  ],
  templateUrl: './communication.html',
  styleUrl: './communication.css'
})
export class Communication implements OnInit {
  @ViewChild(CommunicationTable) communicationTable?: CommunicationTable;

  totalMessages = 0;
  unreadMessages = 0;
  sentToday = 0;
  attachmentsCount = 0;

  private communicationService = inject(CommunicationService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadSummaryMetrics();
  }

  loadSummaryMetrics(): void {
    this.communicationService.getMessages().subscribe({
      next: (messages) => {
        this.totalMessages = messages.length;
        this.unreadMessages = messages.filter(m => !m.is_read).length;
        const todayStr = new Date().toISOString().substring(0, 10);
        this.sentToday = messages.filter(m => m.sent_at && m.sent_at.substring(0, 10) === todayStr).length;
        this.attachmentsCount = 0;
        this.cdr.markForCheck();
      },
      error: () => {
        this.totalMessages = 0;
        this.unreadMessages = 0;
        this.sentToday = 0;
        this.attachmentsCount = 0;
        this.cdr.markForCheck();
      }
    });
  }

  onMessageSent(): void {
    this.loadSummaryMetrics();
    if (this.communicationTable) {
      this.communicationTable.loadMessages();
    }
  }
}