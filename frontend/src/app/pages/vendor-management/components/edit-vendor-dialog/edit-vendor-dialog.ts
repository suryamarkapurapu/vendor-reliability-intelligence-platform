import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-edit-vendor-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule
  ],
  templateUrl: './edit-vendor-dialog.html',
  styleUrl: './edit-vendor-dialog.css'
})
export class EditVendorDialog {

  private fb = inject(FormBuilder);

  private dialogRef = inject(MatDialogRef<EditVendorDialog>);

  data = inject(MAT_DIALOG_DATA);

  vendorForm = this.fb.group({

    name: [this.data.name, Validators.required],

    category: [this.data.categoryId || this.data.category, Validators.required],

    contact: [this.data.contact, Validators.required],

    email: [this.data.email, [Validators.required, Validators.email]],

    status: [this.data.status, Validators.required]

  });

  save() {

    this.dialogRef.close(this.vendorForm.value);

  }

}