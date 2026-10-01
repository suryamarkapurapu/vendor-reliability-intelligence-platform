import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.css'
})
export class ForgotPassword {

  forgotPasswordForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService
  ) {

    this.forgotPasswordForm = this.fb.group({

      email: [
        '',
        [
          Validators.required,
          Validators.email
        ]
      ]

    });

  }

  sendResetLink(): void {

    if (this.forgotPasswordForm.invalid) {

      this.forgotPasswordForm.markAllAsTouched();

      return;

    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.authService.forgotPassword({
      email: this.forgotPasswordForm.value.email
    }).subscribe({
      next: (response) => {
        console.log('FORGOT PASSWORD RESPONSE:', response);
  this.loading = false;
  console.log('LOADING AFTER RESPONSE:', this.loading);
  this.successMessage =
    response.message ??
    'Password reset link generated. Please check your email or development server console.';
},
      error: (error: HttpErrorResponse) => {
        console.error('FORGOT PASSWORD ERROR:', error);
        this.loading = false;
        this.errorMessage = this.extractErrorMessage(
          error,
          'Unable to process password reset request.'
        );
      }
    });

  }

  private extractErrorMessage(error: HttpErrorResponse, fallback: string): string {
    const detail = error.error?.detail;

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      return detail
        .map((item) => item?.msg)
        .filter(Boolean)
        .join(' ');
    }

    return fallback;
  }

}
