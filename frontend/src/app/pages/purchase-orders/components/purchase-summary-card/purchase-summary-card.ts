import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-purchase-summary-card',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './purchase-summary-card.html',
  styleUrl: './purchase-summary-card.css'
})
export class PurchaseSummaryCard {

  @Input() title = '';

  @Input() value = 0;

  @Input() icon = '';
}