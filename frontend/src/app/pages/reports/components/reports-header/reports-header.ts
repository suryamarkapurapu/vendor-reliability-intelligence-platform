import { Component, EventEmitter, Output } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-reports-header',
  standalone: true,

  imports: [
    MatButtonModule,
    MatIconModule
  ],

  templateUrl: './reports-header.html',
  styleUrl: './reports-header.css'
})
export class ReportsHeader {

  @Output() generateReport = new EventEmitter<void>();
  @Output() exportReportsEvent = new EventEmitter<void>();

  openGenerateReport(): void {
    this.generateReport.emit();
  }

  exportReports(): void {
    this.exportReportsEvent.emit();
  }

}
