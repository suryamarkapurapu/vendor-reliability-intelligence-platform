import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef
} from '@angular/material/dialog';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';

export interface VendorReliabilityDialogData {
  vendor: string;
  reliabilityScore: number;
  deliveryPerformance: number;
  qualityRating: number;
  riskLevel: string;
  rank: number;

  communication: number;
  compliance: number;
  issueResolution: number;
}

@Component({
  selector: 'app-vendor-reliability-dialog',
  standalone: true,

  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule
  ],

  templateUrl: './vendor-reliability-dialog.html',
  styleUrl: './vendor-reliability-dialog.css'
})
export class VendorReliabilityDialog {

  constructor(
    @Inject(MAT_DIALOG_DATA)
    public data: VendorReliabilityDialogData,

    private dialogRef:
      MatDialogRef<VendorReliabilityDialog>
  ) {}

  close(): void {
    this.dialogRef.close();
  }

}