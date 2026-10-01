import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getDashboardMetrics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/analytics/dashboard`);
  }

  getProcurementAnalytics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/analytics/procurement`);
  }

  getVendorAnalytics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/analytics/vendors`);
  }

  getInvoiceAnalytics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/analytics/invoices`);
  }

  getDeliveryAnalytics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/analytics/deliveries`);
  }
}
