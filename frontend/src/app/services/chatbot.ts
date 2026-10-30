
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChatResponse {
  reply: string;
}

@Injectable({
  providedIn: 'root',
})
export class Chatbot {

  private readonly apiUrl = 'http://127.0.0.1:8000/api/v1/chat/';

  constructor(private http: HttpClient) {}

  sendMessage(message: string): Observable<ChatResponse> {

    return this.http.post<ChatResponse>(
      this.apiUrl,
      { message: message }
    );

  }
}
