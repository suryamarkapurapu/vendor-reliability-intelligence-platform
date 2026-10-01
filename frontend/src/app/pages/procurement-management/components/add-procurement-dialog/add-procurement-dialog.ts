import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';

@Component({
  selector: 'app-add-procurement-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule
  ],
  templateUrl: './add-procurement-dialog.html',
  styleUrl: './add-procurement-dialog.css'
})
export class AddProcurementDialog {

  private fb = inject(FormBuilder);

  private dialogRef = inject(MatDialogRef<AddProcurementDialog>);

  procurementForm = this.fb.group({

    requestId:['', Validators.required],

    item:['', Validators.required],

    vendor:['', Validators.required],

    quantity:[1, Validators.required],

    budget:[0, Validators.required],

    requiredDate:['', Validators.required],

    priority:['Medium', Validators.required],

    status:['Pending', Validators.required],

    description:['']

  });

  save(){

    if(this.procurementForm.invalid){

      this.procurementForm.markAllAsTouched();

      return;

    }

    this.dialogRef.close(this.procurementForm.value);

  }

  cancel(){

    this.dialogRef.close();

  }

}