import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';

import { SettingsService } from '../../../../services/settings.service';

@Component({
  selector: 'app-preference-settings',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule
  ],
  templateUrl: './preference-settings.html',
  styleUrl: './preference-settings.css'
})
export class PreferenceSettings implements OnInit {
  private fb = inject(FormBuilder);
  private settingsService = inject(SettingsService);
  private cdr = inject(ChangeDetectorRef);

  loading = false;
  saving = false;
  message = '';
  error = '';

  preferenceForm = this.fb.group({
    language: ['English'],
    timezone: ['Asia/Kolkata'],
    currency: ['INR']
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
        this.preferenceForm.patchValue({
          language: data.language || 'English',
          timezone: data.timezone || 'Asia/Kolkata',
          currency: data.preferred_currency || 'INR'
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
      language: this.preferenceForm.value.language,
      timezone: this.preferenceForm.value.timezone,
      preferred_currency: this.preferenceForm.value.currency
    };

    this.settingsService.updateSettings(payload).subscribe({
      next: () => {
        this.saving = false;
        this.message = 'User preferences saved successfully.';
        this.cdr.markForCheck();
      },
      error: () => {
        this.saving = false;
        this.error = 'Failed to save user preferences.';
        this.cdr.markForCheck();
      }
    });
  }
}