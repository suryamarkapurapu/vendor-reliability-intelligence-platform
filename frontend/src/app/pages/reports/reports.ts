import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Navbar } from '../../layouts/navbar/navbar';
import { Sidebar } from '../../layouts/sidebar/sidebar';

import { ReportsHeader } from './components/reports-header/reports-header';
import { ReportsToolbar } from './components/reports-toolbar/reports-toolbar';
import { ReportsTable } from './components/reports-table/reports-table';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import {
  GenerateReportDialog
} from './components/generate-report-dialog/generate-report-dialog';
import { ReportService } from '../../services/report.service';
import {
  ExportReportDialog
} from './components/export-report-dialog/export-report-dialog';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [
    CommonModule,
    Navbar,
    Sidebar,
    ReportsHeader,
    ReportsToolbar,
    ReportsTable,
    MatDialogModule
  ],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})

export class Reports {

  constructor(
    private dialog: MatDialog,
    private reportService: ReportService
  ) {}

  openGenerateReport(): void {
    const dialogRef = this.dialog.open(
      GenerateReportDialog,
      {
        width: '500px'
      }
    );

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (result.format === 'Excel') {
          alert('XLSX export format is not supported by backend. Please select PDF, CSV, or JSON format.');
          return;
        }

        const category = this.mapReportCategory(result.reportType);
        const fileType = this.mapFileType(result.format);
        this.reportService.exportReport(category, fileType).subscribe({
          next: (response) => {
            if (!response || !response.download_token) {
              console.error('No download_token returned in export response metadata.');
              return;
            }
            this.reportService.downloadReportFile(response.download_token).subscribe({
              next: (blob) => {
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                const safeName = (result.reportName || 'generated_report').replace(/[^a-zA-Z0-9_-]/g, '_');
                const ext = fileType === 'pdf' ? 'pdf' : (fileType === 'csv' ? 'csv' : 'json');
                link.download = `${safeName}.${ext}`;
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
    });
  }

  private mapReportCategory(reportType: string): string {
    const categories: Record<string, string> = {
      'Vendor Performance': 'vendor_performance',
      'Procurement Summary': 'procurement',
      'Purchase Order Summary': 'purchase_order',
      'Contract Status': 'contract',
      'Vendor Risk Analysis': 'compliance',
      'Spend Analysis': 'procurement'
    };

    return categories[reportType] ?? 'procurement';
  }

  private mapFileType(format: string): string {
    const fileTypes: Record<string, string> = {
      PDF: 'pdf',
      Excel: 'xlsx',
      CSV: 'csv'
    };

    return fileTypes[format] ?? 'pdf';
  }

  openExportReport(): void {

  const dialogRef = this.dialog.open(
    ExportReportDialog,
    {
      width: '500px'
    }
  );

  dialogRef.afterClosed().subscribe(result => {

    if (!result) {
      return;
    }

    const category = this.mapReportCategory(
      result.reportType
    );

    const fileType = this.mapFileType(
      result.format
    );

    this.reportService.exportReport(
      category,
      fileType
    ).subscribe({

      next: (response) => {

        if (!response || !response.download_token) {

          console.error(
            'No download_token returned in export response metadata.'
          );

          return;
        }

        this.reportService
          .downloadReportFile(response.download_token)
          .subscribe({

            next: (blob) => {

              const url =
                window.URL.createObjectURL(blob);

              const link =
                document.createElement('a');

              link.href = url;

              const safeName =
                result.reportType
                  .replace(
                    /[^a-zA-Z0-9_-]/g,
                    '_'
                  );

              const ext =
                fileType === 'pdf'
                  ? 'pdf'
                  : fileType === 'csv'
                    ? 'csv'
                    : 'json';

              link.download =
                `${safeName}.${ext}`;

              link.click();

              window.URL.revokeObjectURL(url);
            },

            error: (err) => {

              console.error(
                'Error streaming report file:',
                err
              );

            }

          });

      },

      error: (err) => {

        console.error(
          'Error generating report export metadata:',
          err
        );

      }

    });

  });

}
}
