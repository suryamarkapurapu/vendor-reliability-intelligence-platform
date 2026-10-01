import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  MAT_DIALOG_DATA,
  MatDialogModule
} from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-view-procurement-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule
  ],
  templateUrl: './view-procurement-dialog.html',
  styleUrl: './view-procurement-dialog.css'
})
export class ViewProcurementDialog {

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

}