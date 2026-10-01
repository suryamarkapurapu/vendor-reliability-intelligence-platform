import { Component, OnInit, ViewChild, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';
import { SettingsHeader } from './components/settings-header/settings-header';
import { CompanySettings } from './components/company-settings/company-settings';
import { SecuritySettings } from './components/security-settings/security-settings';
import { SettingsService } from '../../services/settings.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    Navbar,
    Sidebar,
    SettingsHeader,
    CompanySettings,
    SecuritySettings
  ],
  templateUrl: './settings.html',
  styleUrl: './settings.css'
})
export class Settings implements OnInit {

  private settingsService = inject(SettingsService);
  private cdr = inject(ChangeDetectorRef);

  @ViewChild(CompanySettings) companyComp?: CompanySettings;
  @ViewChild(SecuritySettings) secComp?: SecuritySettings;

  isSaving = false;
  saveMessage = '';

  ngOnInit(): void {
    this.settingsService.getSettings().subscribe();
  }

  onSaveSettings(): void {
    this.isSaving = true;
    this.saveMessage = 'Saving settings...';
    this.cdr.markForCheck();

    const companyVal = this.companyComp?.companyForm?.value || {};

    const payload: Record<string, any> = {
      timezone: 'Asia/Kolkata',
      preferred_currency: 'INR'
    };

    if (companyVal.companyName) payload['company_name'] = companyVal.companyName;
    if (companyVal.email) payload['company_email'] = companyVal.email;
    if (companyVal.phone) payload['company_phone'] = companyVal.phone;
    if (companyVal.address) payload['company_address'] = companyVal.address;

    this.settingsService.updateSettings(payload).subscribe({
      next: () => {
        this.isSaving = false;
        this.saveMessage = 'Settings saved successfully!';
        if (this.companyComp) this.companyComp.loadSettings();
        if (this.secComp) this.secComp.loadSettings();
        this.cdr.markForCheck();
        setTimeout(() => {
          this.saveMessage = '';
          this.cdr.markForCheck();
        }, 3000);
      },
      error: () => {
        this.isSaving = false;
        this.saveMessage = 'Error saving settings.';
        this.cdr.markForCheck();
        setTimeout(() => {
          this.saveMessage = '';
          this.cdr.markForCheck();
        }, 3000);
      }
    });
  }
}