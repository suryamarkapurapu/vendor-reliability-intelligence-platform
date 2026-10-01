import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-performance-summary',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './performance-summary.html',
  styleUrl: './performance-summary.css'
})
export class PerformanceSummary {

  @Input() title: string = '';

  @Input() value: string | number = '';

  @Input() icon: string = '';

}