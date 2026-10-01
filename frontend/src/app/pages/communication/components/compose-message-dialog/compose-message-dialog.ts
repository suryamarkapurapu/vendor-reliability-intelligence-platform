import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { VendorService } from '../../../../services/vendor.service';

@Component({
  selector: 'app-compose-message-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './compose-message-dialog.html',
  styleUrl: './compose-message-dialog.css'
})
export class ComposeMessageDialog implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ComposeMessageDialog>);
  private vendorService = inject(VendorService);
  private cdr = inject(ChangeDetectorRef);

  vendors: any[] = [];
  isLoadingVendors = false;

  messageForm = this.fb.group({
    vendor: ['', Validators.required],
    subject: ['', Validators.required],
    type: ['Email', Validators.required],
    message: ['', Validators.required],
    emailNotification: [true]
  });

  selectedFile: File | null = null;

  ngOnInit(): void {
    this.isLoadingVendors = true;
    this.vendorService.getVendors().subscribe({
      next: (data) => {
        this.vendors = data;
        if (this.vendors.length > 0) {
          this.messageForm.patchValue({ vendor: this.vendors[0].vendor_id });
        }
        this.isLoadingVendors = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.vendors = [];
        this.isLoadingVendors = false;
        this.cdr.markForCheck();
      }
    });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
    }
  }

  sendMessage() {
    if (this.messageForm.valid) {
      this.dialogRef.close({
        ...this.messageForm.value,
        attachment: this.selectedFile?.name
      });
    }
  }
}