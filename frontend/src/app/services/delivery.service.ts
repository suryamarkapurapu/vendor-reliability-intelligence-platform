import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export interface DeliveryCreate {
  po_id: string;
  tracking_number?: string;
  carrier?: string;
  expected_date?: string;
  remarks?: string;
}

@Injectable({
  providedIn: 'root'
})
export class DeliveryService {

  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getDeliveries(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/deliveries`
    );
  }

  createDelivery(data: DeliveryCreate): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/deliveries`,
      data
    );
  }

  dispatchDelivery(deliveryId: string): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/deliveries/${deliveryId}/dispatch`,
      {}
    );
  }

  markDelivered(deliveryId: string): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/deliveries/${deliveryId}/deliver`,
      {}
    );
  }

  markDelayed(
    deliveryId: string,
    newExpectedDate?: string,
    remarks?: string
  ): Observable<any> {

    const params: any = {};

    if (newExpectedDate) {
      params.new_expected_date = newExpectedDate;
    }

    if (remarks) {
      params.remarks = remarks;
    }

    return this.http.post<any>(
      `${this.apiUrl}/deliveries/${deliveryId}/delay`,
      {},
      { params }
    );
  }

  markReturned(
    deliveryId: string,
    remarks?: string
  ): Observable<any> {

    const params: any = {};

    if (remarks) {
      params.remarks = remarks;
    }

    return this.http.post<any>(
      `${this.apiUrl}/deliveries/${deliveryId}/return`,
      {},
      { params }
    );
  }
}