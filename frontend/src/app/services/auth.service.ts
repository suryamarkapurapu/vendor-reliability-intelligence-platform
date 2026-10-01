import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';

import { LoginRequest, LoginResponse, RegisterRequest, UserResponse } from '../models/auth.model';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = API_BASE_URL;
  private router = inject(Router);

  constructor(private http: HttpClient) {}

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/auth/login`,
      credentials
    );
  }

  register(data: RegisterRequest): Observable<UserResponse> {
    return this.http.post<UserResponse>(
      `${this.apiUrl}/auth/register`,
      data
    );
  }

  forgotPassword(data: { email: string }): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/auth/forgot-password`,
      data
    );
  }

  resetPassword(data: { token: string; new_password: string }): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/auth/reset-password`,
      data
    );
  }

  saveToken(token: string, rememberMe: boolean = false): void {
    if (rememberMe) {
      localStorage.setItem('token', token);
      sessionStorage.removeItem('token');
    } else {
      sessionStorage.setItem('token', token);
      localStorage.removeItem('token');
    }
  }

  getToken(): string | null {
    return localStorage.getItem('token') || sessionStorage.getItem('token');
  }

  logout(): void {
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return this.getToken() !== null;
  }

  getMe(): Observable<UserResponse> {
    return this.http.get<UserResponse>(`${this.apiUrl}/auth/me`);
  }
}
