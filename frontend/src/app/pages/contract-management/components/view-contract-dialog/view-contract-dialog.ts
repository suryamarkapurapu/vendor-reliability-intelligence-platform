import { Component, Inject } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';

import {
  MAT_DIALOG_DATA,
  MatDialogModule
} from '@angular/material/dialog';

import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-view-contract-dialog',
  standalone: true,
  imports: [
    CommonModule,
    DecimalPipe,
    MatDialogModule,
    MatButtonModule
  ],
  templateUrl: './view-contract-dialog.html',
  styleUrl: './view-contract-dialog.css'
})
export class ViewContractDialog {

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

}