import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class VendorService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getVendors(skip = 0, limit = 100): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/vendors?skip=${skip}&limit=${limit}`);
  }

  getVendorById(vendorId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/vendors/${vendorId}`);
  }

  createVendor(vendorData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/vendors`, vendorData);
  }

  updateVendor(vendorId: string, vendorData: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/vendors/${vendorId}`, vendorData);
  }

  deleteVendor(vendorId: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/vendors/${vendorId}`);
  }

  approveVendor(vendorId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/vendors/${vendorId}/approve`, {});
  }
}
