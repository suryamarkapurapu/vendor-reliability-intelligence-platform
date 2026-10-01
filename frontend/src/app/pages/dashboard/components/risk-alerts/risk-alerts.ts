import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { VendorPerformanceService } from '../../../../services/vendor-performance.service';

interface Risk {
  vendor: string;
  risk: string;
}

@Component({
  selector: 'app-risk-alerts',
  standalone: true,
  imports: [MatCardModule, MatTableModule],
  templateUrl: './risk-alerts.html',
  styleUrl: './risk-alerts.css'
})
export class RiskAlerts implements OnInit {
  displayedColumns: string[] = ['vendor', 'risk'];
  dataSource: Risk[] = [];
  hasError = false;
  errorMessage = '';

  constructor(
    private vendorPerformanceService: VendorPerformanceService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.vendorPerformanceService.getRankings(0, 5).subscribe({
      next: (rankings) => {
        this.hasError = false;
        this.dataSource = rankings.map((ranking) => ({
          vendor: ranking.vendor_name,
          risk: this.getRiskLevel(Number(ranking.overall_score ?? 0))
        }));
        this.cdr.markForCheck();
      },
      error: () => {
        this.hasError = true;
        this.errorMessage = 'Unable to load risk alerts';
        this.dataSource = [];
        this.cdr.markForCheck();
      }
    });
  }

  private getRiskLevel(score: number): string {
    if (score >= 80) {
      return 'Low';
    }

    if (score >= 60) {
      return 'Medium';
    }

    return 'High';
  }
}
