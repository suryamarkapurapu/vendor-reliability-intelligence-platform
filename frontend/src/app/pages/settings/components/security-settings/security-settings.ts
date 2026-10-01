import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

import { SettingsService } from '../../../../services/settings.service';

@Component({
  selector: 'app-security-settings',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  templateUrl: './security-settings.html',
  styleUrl: './security-settings.css'
})
export class SecuritySettings implements OnInit {
  private fb = inject(FormBuilder);
  private settingsService = inject(SettingsService);
  private cdr = inject(ChangeDetectorRef);

  loading = false;
  saving = false;
  message = '';
  error = '';

  securityForm = this.fb.group({
    currentPassword: [''],
    newPassword: [''],
    confirmPassword: ['']
  });

  ngOnInit(): void {
    this.loadSettings();
  }

  loadSettings(): void {
    this.loading = false;
    this.cdr.markForCheck();
  }

  saveSettings(): void {
    this.saving = true;
    this.message = '';
    this.error = '';
    this.cdr.markForCheck();

    setTimeout(() => {
      this.saving = false;
      this.message = 'Security settings updated successfully.';
      this.cdr.markForCheck();
    }, 500);
  }
}