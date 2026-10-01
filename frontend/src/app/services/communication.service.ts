import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class CommunicationService {
  private apiUrl = API_BASE_URL;

  constructor(private http: HttpClient) {}

  getMessages(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/communications`);
  }

  sendMessage(data: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/communications`, data);
  }
  markAsRead(messageId: string): Observable<any> {
  return this.http.patch<any>(
    `${this.apiUrl}/communications/${messageId}/read`,
    {}
  );
}
}