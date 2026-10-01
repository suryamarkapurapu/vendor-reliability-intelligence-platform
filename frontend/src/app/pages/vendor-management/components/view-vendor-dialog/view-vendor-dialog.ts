import { Component, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-view-vendor-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule
  ],
  templateUrl: './view-vendor-dialog.html',
  styleUrl: './view-vendor-dialog.css'
})
export class ViewVendorDialog {

  data = inject(MAT_DIALOG_DATA);

}