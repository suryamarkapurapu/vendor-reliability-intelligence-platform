import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';

import { SettingsService } from '../../../../services/settings.service';

@Component({
  selector: 'app-notification-settings',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatSlideToggleModule,
    MatButtonModule
  ],
  templateUrl: './notification-settings.html',
  styleUrl: './notification-settings.css'
})
export class NotificationSettings implements OnInit {
  private fb = inject(FormBuilder);
  private settingsService = inject(SettingsService);
  private cdr = inject(ChangeDetectorRef);

  loading = false;
  saving = false;
  message = '';
  error = '';

  notificationForm = this.fb.group({
    email: [true],
    vendorAlerts: [true],
    contractAlerts: [true]
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
        this.notificationForm.patchValue({
          email: data.email_notifications,
          vendorAlerts: data.vendor_alerts,
          contractAlerts: data.contract_alerts
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
      email_notifications: Boolean(this.notificationForm.value.email),
      sms_notifications: false,
      vendor_alerts: Boolean(this.notificationForm.value.vendorAlerts),
      contract_alerts: Boolean(this.notificationForm.value.contractAlerts)
    };

    this.settingsService.updateSettings(payload).subscribe({
      next: () => {
        this.saving = false;
        this.message = 'Notification preferences saved successfully.';
        this.cdr.markForCheck();
      },
      error: () => {
        this.saving = false;
        this.error = 'Failed to save notification preferences.';
        this.cdr.markForCheck();
      }
    });
  }
}