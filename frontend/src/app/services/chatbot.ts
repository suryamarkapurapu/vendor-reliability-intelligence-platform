
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

  private readonly apiUrl = 'https://vendor-reliability-intelligence-platform-gn0z.onrender.com/api/v1/chat/';

  constructor(private http: HttpClient) {}

  sendMessage(message: string): Observable<ChatResponse> {

    return this.http.post<ChatResponse>(
      this.apiUrl,
      { message: message }
    );

  }
}
