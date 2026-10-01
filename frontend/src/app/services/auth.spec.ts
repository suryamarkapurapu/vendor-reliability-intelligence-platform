import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  LoginRequest,
  LoginResponse
} from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://127.0.0.1:8000/api/v1';

  constructor(private http: HttpClient) {}


  login(credentials: LoginRequest): Observable<LoginResponse> {

    return this.http.post<LoginResponse>(
      `${this.apiUrl}/auth/login`,
      credentials
    );

  }


  saveToken(token: string): void {

    localStorage.setItem(
      'token',
      token
    );

  }


  getToken(): string | null {

    return localStorage.getItem('token');

  }


  logout(): void {

    localStorage.removeItem('token');

  }


  isLoggedIn(): boolean {

    return this.getToken() !== null;

  }

}