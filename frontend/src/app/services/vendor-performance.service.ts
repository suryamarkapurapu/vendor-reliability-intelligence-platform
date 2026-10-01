import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class VendorPerformanceService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getRankings(skip = 0, limit = 100): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/vendor-performance/rankings?skip=${skip}&limit=${limit}`
    );
  }

  createRating(ratingData: {
    vendor_id: string;
    purchase_order_id?: string | null;
    quality_rating: number;
    delivery_rating: number;
    communication_rating: number;
    comments?: string;
  }): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/vendor-performance/ratings`,
      ratingData
    );
  }
}