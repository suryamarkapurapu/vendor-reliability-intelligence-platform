import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import {
  MatDialogRef
} from '@angular/material/dialog';

@Component({
  selector: 'app-add-vendor-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
  ],
  templateUrl: './add-vendor-dialog.html',
  styleUrl: './add-vendor-dialog.css'
})
export class AddVendorDialog {

  private fb = inject(FormBuilder);

  private dialogRef = inject(MatDialogRef<AddVendorDialog>);

  vendorForm = this.fb.group({
    vendorName: ['', Validators.required],
    category: [1, Validators.required],
    vendorType: [''],
    contact: [''],
    email: [''],
    address: [''],
    status: ['pending']
  });

  saveVendor() {

  if (this.vendorForm.invalid) {

    this.vendorForm.markAllAsTouched();

    return;

  }

  this.dialogRef.close(this.vendorForm.value);

}
}
