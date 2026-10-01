import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { ChartConfiguration } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { ContractService } from '../../../../services/contract.service';

@Component({
  selector: 'app-contract-chart',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    BaseChartDirective
  ],
  templateUrl: './contract-chart.html',
  styleUrl: './contract-chart.css'
})
export class ContractChart implements OnInit {
  private contractService = inject(ContractService);
  private cdr = inject(ChangeDetectorRef);

  hasData = false;

  pieChartData: ChartConfiguration<'pie'>['data'] = {
    labels: [],
    datasets: []
  };

  pieChartOptions: ChartConfiguration<'pie'>['options'] = {
    responsive: true,
    maintainAspectRatio: false
  };

  ngOnInit(): void {
    this.contractService.getContracts().subscribe({
      next: (contracts) => {
        let active = 0;
        let expiring = 0;
        let expired = 0;

        contracts.forEach((c: any) => {
          const status = String(c.status || '').toUpperCase();
          if (status === 'ACTIVE') {
            active++;
          } else if (status === 'EXPIRING' || status === 'PENDING') {
            expiring++;
          } else if (status === 'EXPIRED' || status === 'TERMINATED') {
            expired++;
          } else {
            active++;
          }
        });

        if (active + expiring + expired > 0) {
          this.hasData = true;
          this.pieChartData = {
            labels: ['Active', 'Expiring', 'Expired'],
            datasets: [
              {
                data: [active, expiring, expired],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
              }
            ]
          };
        } else {
          this.hasData = false;
          this.pieChartData = { labels: [], datasets: [] };
        }
        this.cdr.markForCheck();
      },
      error: () => {
        this.hasData = false;
        this.pieChartData = { labels: [], datasets: [] };
        this.cdr.markForCheck();
      }
    });
  }
}