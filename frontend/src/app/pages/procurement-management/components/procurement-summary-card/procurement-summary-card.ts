import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-procurement-summary-card',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './procurement-summary-card.html',
  styleUrl: './procurement-summary-card.css'
})
export class ProcurementSummaryCard {

  @Input() title: string = '';

  @Input() value: number | string = 0;

  @Input() icon = '';
}