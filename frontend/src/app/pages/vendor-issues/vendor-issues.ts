import { Component, OnInit, inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';

import { VendorIssuesService } from '../../services/vendor-issues.service';
import { VendorService } from '../../services/vendor.service';
import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';

@Component({
  selector: 'app-vendor-issues',
  standalone: true,
  imports: [
    Navbar,
    Sidebar,
    CommonModule,
    DatePipe,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatTableModule
  ],
  templateUrl: './vendor-issues.html',
  styleUrl: './vendor-issues.css'
})
export class VendorIssues implements OnInit {

  private issuesService = inject(VendorIssuesService);
  private vendorService = inject(VendorService);

  vendors: any[] = [];
  issues: any[] = [];

  selectedVendorId = '';
  issueType = '';
  description = '';
  selectedStatus = '';

  loading = false;
  saving = false;
  errorMessage = '';
  successMessage = '';

  displayedColumns = [
    'vendor',
    'issueType',
    'description',
    'status',
    'createdAt'
  ];

  ngOnInit(): void {
    this.loadVendors();
    this.loadIssues();
  }

  loadVendors(): void {
    this.vendorService.getVendors(0, 100).subscribe({
      next: (data) => {
        this.vendors = data;
      },
      error: (error) => {
  console.error('Vendor Issues API Error');
  console.error('Status:', error.status);
  console.error('Status Text:', error.statusText);
  console.error('URL:', error.url);
  console.error('Error:', error.error);

  this.errorMessage =
    error?.error?.detail ||
    `Unable to load vendor issues. HTTP ${error.status}`;

  this.loading = false;
},
    });
  }

  loadIssues(): void {
    this.loading = true;

    this.issuesService.getIssues(
      0,
      100,
      this.selectedVendorId || undefined,
      this.selectedStatus || undefined
    ).subscribe({
      next: (data) => {
        this.issues = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Failed to load vendor issues', error);
        this.errorMessage = 'Unable to load vendor issues.';
        this.loading = false;
      }
    });
  }

  createIssue(): void {

    this.errorMessage = '';
    this.successMessage = '';

    if (!this.selectedVendorId) {
      this.errorMessage = 'Please select a vendor.';
      return;
    }

    if (!this.issueType.trim()) {
      this.errorMessage = 'Please enter an issue type.';
      return;
    }

    this.saving = true;

    const issueData = {
      vendor_id: this.selectedVendorId,
      issue_type: this.issueType.trim(),
      description: this.description.trim() || null
    };

    this.issuesService.createIssue(issueData).subscribe({
      next: () => {

        this.successMessage = 'Vendor issue created successfully.';

        this.selectedVendorId = '';
        this.issueType = '';
        this.description = '';

        this.saving = false;

        this.loadIssues();
      },
      error: (error) => {

        console.error('Failed to create vendor issue', error);

        this.errorMessage =
          error?.error?.detail ||
          'Unable to create vendor issue.';

        this.saving = false;
      }
    });
  }

  filterIssues(): void {
    this.loadIssues();
  }

  clearFilters(): void {
    this.selectedVendorId = '';
    this.selectedStatus = '';
    this.loadIssues();
  }

  getVendorName(vendorId: string): string {

    const vendor = this.vendors.find(
      v => v.vendor_id === vendorId
    );

    return vendor?.company_name || vendor?.vendor_name || vendorId;
  }
}