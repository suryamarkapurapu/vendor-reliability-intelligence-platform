import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class PurchaseOrderService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getPurchaseOrders(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/procurement/purchase-orders`);
  }

  createPurchaseOrder(data: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/purchase-orders`, data);
  }

  approvePurchaseOrder(poId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/purchase-orders/${poId}/approve`, {});
  }

  deliverPurchaseOrder(poId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/purchase-orders/${poId}/deliver`, {});
  }

  completePurchaseOrder(poId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/procurement/purchase-orders/${poId}/complete`, {});
  }
}
