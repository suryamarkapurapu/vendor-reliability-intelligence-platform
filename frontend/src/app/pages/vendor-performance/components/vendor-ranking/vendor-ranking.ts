import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import {
  VendorReliabilityDialog
} from '../vendor-reliability-dialog/vendor-reliability-dialog';
import { VendorPerformanceService } from '../../../../services/vendor-performance.service';

export interface VendorReliability {

  vendor: string;

  reliabilityScore: number;

  deliveryPerformance: number;

  qualityRating: number;

  riskLevel: string;

  rank: number;
}

@Component({
  selector: 'app-vendor-ranking',

  standalone: true,

  imports: [
    MatTableModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatChipsModule,
    MatTooltipModule,
    MatDialogModule
  ],

  templateUrl: './vendor-ranking.html',
  styleUrl: './vendor-ranking.css'
})
export class VendorRanking implements OnInit {

  displayedColumns: string[] = [
    'rank',
    'vendor',
    'reliabilityScore',
    'deliveryPerformance',
    'qualityRating',
    'riskLevel',
    'actions'
  ];


  dataSource: VendorReliability[] = [];

constructor(
  private dialog: MatDialog,
  private vendorPerformanceService: VendorPerformanceService,
  private cdr: ChangeDetectorRef
) {}

ngOnInit(): void {
  this.vendorPerformanceService.getRankings().subscribe({
    next: (rankings) => {
      this.dataSource = rankings.map((ranking) => ({
        vendor: ranking.vendor_name,
        reliabilityScore: Number(ranking.overall_score ?? 0),
        deliveryPerformance: Number(ranking.on_time_delivery_rate ?? 0),
        qualityRating: Number(ranking.average_overall_rating ?? 0),
        riskLevel: Number(ranking.overall_score ?? 0) >= 80 ? 'Low' : Number(ranking.overall_score ?? 0) >= 60 ? 'Medium' : 'High',
        rank: ranking.rank
      }));
      this.cdr.markForCheck();
    },
    error: () => {
      this.dataSource = [];
      this.cdr.markForCheck();
    }
  });
}
  viewVendor(vendor: VendorReliability): void {

  this.dialog.open(VendorReliabilityDialog, {

    width: '650px',

    maxWidth: '95vw',

    data: {

      ...vendor,

      communication:
        vendor.qualityRating,

      compliance:
        vendor.reliabilityScore,

      issueResolution:
        vendor.deliveryPerformance

    }

  });

  }

}
