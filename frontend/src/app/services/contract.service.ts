import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class ContractService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getContracts(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/contracts`);
  }

  createContract(data: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/contracts`, data);
  }

  updateContract(contractId: string, data: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/contracts/${contractId}`, data);
  }
}
