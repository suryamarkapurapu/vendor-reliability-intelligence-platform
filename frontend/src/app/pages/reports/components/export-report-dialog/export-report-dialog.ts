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
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-export-report-dialog',
  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule
  ],

  templateUrl: './export-report-dialog.html',
  styleUrl: './export-report-dialog.css'
})
export class ExportReportDialog {

  exportForm;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<ExportReportDialog>
  ) {

    this.exportForm = this.fb.group({

      reportType: [
        '',
        Validators.required
      ],

      format: [
        'PDF',
        Validators.required
      ]

    });

  }

  exportReport(): void {

    if (this.exportForm.invalid) {
      return;
    }

    const result = {
      reportType: this.exportForm.value.reportType,
      format: this.exportForm.value.format
    };

    this.dialogRef.close(result);
  }

  cancel(): void {
    this.dialogRef.close();
  }
}