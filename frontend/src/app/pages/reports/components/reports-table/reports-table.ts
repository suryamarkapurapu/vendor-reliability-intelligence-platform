import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { inject } from '@angular/core';

import { MatDialog } from '@angular/material/dialog';

import { ViewReportDialog } from '../view-report-dialog/view-report-dialog';

import { MatMenuModule } from '@angular/material/menu';
import { MatChipsModule } from '@angular/material/chips';
import { ReportService } from '../../../../services/report.service';

interface Report{

  reportName:string;

  category:string;

  generatedDate:string;

  status:string;

}

@Component({
  selector:'app-reports-table',
  standalone:true,
  imports:[
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatChipsModule
  ],
  templateUrl:'./reports-table.html',
  styleUrl:'./reports-table.css'
})
export class ReportsTable implements OnInit{

  displayedColumns=[
    'reportName',
    'category',
    'generatedDate',
    'status',
    'actions'
  ];

  dataSource:Report[]=[];
private dialog = inject(MatDialog);
private reportService = inject(ReportService);
private cdr = inject(ChangeDetectorRef);

ngOnInit(): void {
  this.reportService.getReportHistory().subscribe({
    next: (response) => {
      this.dataSource = (response.items ?? []).map((report: any) => ({
        reportName: report.report_name,
        category: this.formatCategory(report.category),
        generatedDate: report.generated_date,
        status: report.status
      }));
      this.cdr.markForCheck();
    },
    error: () => {
      this.dataSource = [];
      this.cdr.markForCheck();
    }
  });
}
viewReport(report: Report): void {

  this.dialog.open(ViewReportDialog, {
    width: '600px',
    data: report
  });

}

downloadReport(report: Report): void {
  const category = report.category.toLowerCase().replace(/\s+/g, '_');
  this.reportService.exportReport(category, 'json').subscribe({
    next: (exp) => {
      if (!exp || !exp.download_token) {
        console.error('No download token returned from export endpoint.');
        return;
      }
      this.reportService.downloadReportFile(exp.download_token).subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          const safeName = (report.reportName || 'report').replace(/[^a-zA-Z0-9_-]/g, '_');
          link.download = `${safeName}_export.json`;
          link.click();
          window.URL.revokeObjectURL(url);
        },
        error: (err) => {
          console.error('Error streaming report file:', err);
        }
      });
    },
    error: (err) => {
      console.error('Error generating report export metadata:', err);
    }
  });
}

private formatCategory(category: string): string {

  const categories: Record<string, string> = {
    vendor_performance: 'Vendor Performance',
    procurement: 'Procurement',
    purchase_order: 'Purchase Order',
    contract: 'Contract',
    compliance: 'Compliance'
  };

  return categories[category] ?? category;
}
}

