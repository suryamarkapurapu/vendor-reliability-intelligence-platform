import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-vendor-summary-card',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './vendor-summary-card.html',
  styleUrl: './vendor-summary-card.css'
})
export class VendorSummaryCard {

  @Input() title = '';

  @Input() value = 0;

  @Input() icon = '';

}