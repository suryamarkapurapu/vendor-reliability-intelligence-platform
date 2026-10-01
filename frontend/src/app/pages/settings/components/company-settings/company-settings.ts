import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

import { SettingsService } from '../../../../services/settings.service';

@Component({
  selector: 'app-company-settings',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatDividerModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './company-settings.html',
  styleUrl: './company-settings.css'
})
export class CompanySettings implements OnInit {
  private fb = inject(FormBuilder);
  private settingsService = inject(SettingsService);
  private cdr = inject(ChangeDetectorRef);

  loading = false;
  saving = false;
  message = '';
  error = '';

  companyForm = this.fb.group({
    companyName: [''],
    email: [''],
    phone: [''],
    address: ['']
  });

  ngOnInit(): void {
    this.loadSettings();
  }

  loadSettings(): void {
    this.loading = true;
    this.cdr.markForCheck();
    this.settingsService.getSettings().subscribe({
      next: (data) => {
        this.loading = false;
        this.companyForm.patchValue({
          companyName: data.company_name,
          email: data.company_email,
          phone: data.company_phone,
          address: data.company_address
        });
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  saveSettings(): void {
    this.saving = true;
    this.message = '';
    this.error = '';
    this.cdr.markForCheck();

    const payload = {
      company_name: this.companyForm.value.companyName,
      company_email: this.companyForm.value.email,
      company_phone: this.companyForm.value.phone,
      company_address: this.companyForm.value.address
    };

    this.settingsService.updateSettings(payload).subscribe({
      next: () => {
        this.saving = false;
        this.message = 'Company settings saved successfully.';
        this.cdr.markForCheck();
      },
      error: () => {
        this.saving = false;
        this.error = 'Failed to save company settings.';
        this.cdr.markForCheck();
      }
    });
  }
}