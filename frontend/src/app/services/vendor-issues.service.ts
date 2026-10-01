import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class VendorIssuesService {

  private apiUrl = `${API_BASE_URL}/vendor-performance`;

  constructor(private http: HttpClient) {}

  getIssues(
    skip = 0,
    limit = 100,
    vendorId?: string,
    status?: string
  ): Observable<any[]> {

    let params = new HttpParams()
      .set('skip', skip)
      .set('limit', limit);

    if (vendorId) {
      params = params.set('vendor_id', vendorId);
    }

    if (status) {
      params = params.set('status', status);
    }

    return this.http.get<any[]>(
      `${this.apiUrl}/issues`,
      { params }
    );
  }

  createIssue(issueData: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/issues`,
      issueData
    );
  }

  updateIssue(
    issueId: string,
    issueData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/issues/${issueId}`,
      issueData
    );
  }
}