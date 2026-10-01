import { Component, Inject } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';

import {
  MAT_DIALOG_DATA,
  MatDialogModule
} from '@angular/material/dialog';

import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-view-purchase-order-dialog',
  standalone: true,
  imports: [
    CommonModule,
    DecimalPipe,
    MatDialogModule,
    MatButtonModule
  ],
  templateUrl: './view-purchase-order-dialog.html',
  styleUrl: './view-purchase-order-dialog.css'
})
export class ViewPurchaseOrderDialog {

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

}