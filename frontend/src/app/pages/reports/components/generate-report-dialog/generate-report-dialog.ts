import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  MatDialogModule,
  MatDialogRef
} from '@angular/material/dialog';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-generate-report-dialog',
  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule
  ],

  templateUrl: './generate-report-dialog.html',
  styleUrl: './generate-report-dialog.css'
})
export class GenerateReportDialog {

  reportForm;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GenerateReportDialog>
  ) {

   this.reportForm = this.fb.group({

  reportName: [
    '',
    Validators.required
  ],

  reportType: [
    '',
    Validators.required
  ],

  fromDate: [
    '',
    Validators.required
  ],

  toDate: [
    '',
    Validators.required
  ],

  format: [
    'PDF',
    Validators.required
  ]

});

  }


  generateReport(): void {

    if (this.reportForm.invalid) {
      return;
    }

    const report = {
  reportName: this.reportForm.value.reportName,
  reportType: this.reportForm.value.reportType,
  fromDate: this.reportForm.value.fromDate,
  toDate: this.reportForm.value.toDate,
  format: this.reportForm.value.format
};

    this.dialogRef.close(report);
  }


  cancel(): void {

    this.dialogRef.close();

  }

}
