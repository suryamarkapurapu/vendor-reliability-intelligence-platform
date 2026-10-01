import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  MAT_DIALOG_DATA,
  MatDialogModule
} from '@angular/material/dialog';

import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-view-report-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule
  ],
  templateUrl: './view-report-dialog.html',
  styleUrl: './view-report-dialog.css'
})
export class ViewReportDialog {

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

}