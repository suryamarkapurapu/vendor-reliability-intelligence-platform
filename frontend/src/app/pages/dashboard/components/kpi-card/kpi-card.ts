import { Component, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [
    DecimalPipe,
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './kpi-card.html',
  styleUrl: './kpi-card.css'
})
export class KpiCard {

  @Input() title = '';

  @Input() value: number = 0;

  @Input() icon = '';

  @Input() currency = false;
}