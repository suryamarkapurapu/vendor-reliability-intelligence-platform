import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-communication-summary-card',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './communication-summary-card.html',
  styleUrl: './communication-summary-card.css'
})
export class CommunicationSummaryCard {

  @Input() title = '';

  @Input() value = 0;

  @Input() icon = '';

}