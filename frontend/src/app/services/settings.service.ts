import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) { }

  getSettings(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/settings`);
  }

  updateSettings(data: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/settings`, data);
  }
}
