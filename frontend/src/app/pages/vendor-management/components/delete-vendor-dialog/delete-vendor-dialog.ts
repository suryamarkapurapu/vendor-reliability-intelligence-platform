import { Component, inject } from '@angular/core';

import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';

import { MatButtonModule } from '@angular/material/button';

@Component({
  selector:'app-delete-vendor-dialog',
  standalone:true,
  imports:[
    MatDialogModule,
    MatButtonModule
  ],
  templateUrl:'./delete-vendor-dialog.html',
  styleUrl:'./delete-vendor-dialog.css'
})
export class DeleteVendorDialog {

  dialogRef = inject(MatDialogRef<DeleteVendorDialog>);

  data = inject(MAT_DIALOG_DATA);

  confirm(){

    this.dialogRef.close(true);

  }

}