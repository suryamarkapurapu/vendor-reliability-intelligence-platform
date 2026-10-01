import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getReportsSummary(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/reports/summary`);
  }

  getReportHistory(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/reports/history`);
  }

  exportReport(category: string, fileType: string): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/reports/export?category=${encodeURIComponent(category)}&file_type=${encodeURIComponent(fileType)}`,
      {}
    );
  }

  downloadReportFile(downloadToken: string): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/reports/download`,
      { download_token: downloadToken },
      { responseType: 'blob' }
    );
  }
}
