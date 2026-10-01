import { Component, Input } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-analytics-summary-card',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './analytics-summary-card.html',
  styleUrl: './analytics-summary-card.css'
})
export class AnalyticsSummaryCard {

  @Input() title='';

  @Input() value='';

  @Input() icon='';

}