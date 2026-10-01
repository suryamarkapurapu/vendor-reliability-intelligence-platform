import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class ProcurementService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getRequests(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/procurement/requests`);
  }

  createRequest(data: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/requests`, data);
  }

  updateRequest(requestId: string, data: any): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/procurement/requests/${requestId}`, data);
  }

  approveRequest(requestId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/requests/${requestId}/approve`, {});
  }

  rejectRequest(requestId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/requests/${requestId}/reject`, {});
  }

  cancelRequest(requestId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/requests/${requestId}/cancel`, {});
  }
}
