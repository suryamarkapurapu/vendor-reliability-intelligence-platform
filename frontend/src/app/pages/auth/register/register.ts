import { Component, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
  AbstractControl,
  ValidationErrors
} from '@angular/forms';

import { Router, RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,

    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCheckboxModule,
    MatIconModule,
    MatSelectModule
  ],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {

  registerForm: FormGroup;

  hidePassword = true;
  hideConfirmPassword = true;
  loading = false;
  errorMessage = '';
  successMessage = '';

  private readonly roleIds: Record<string, number> = {
  'Administrator': 1,
  'Procurement Manager': 2,
  'Supply Chain Manager': 3,
  'Vendor': 4,
  'Finance Officer': 5,
  'Auditor': 6
};

  private cdr = inject(ChangeDetectorRef);

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService
  ) {

    this.registerForm = this.fb.group({

      fullName: ['', Validators.required],

      email: ['', [
        Validators.required,
        Validators.email
      ]],

      phone: ['', [
        Validators.required,
        Validators.pattern('^[0-9]{10}$')
      ]],

      department: ['', Validators.required],

      role: ['', Validators.required],

      password: ['', [
        Validators.required,
        Validators.minLength(8)
      ]],

      confirmPassword: ['', Validators.required],

      terms: [false, Validators.requiredTrue]

    }, {
      validators: this.passwordMatchValidator
    });

  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {

    const password = control.get('password')?.value;

    const confirmPassword = control.get('confirmPassword')?.value;

    if (password !== confirmPassword) {
      return {
        passwordMismatch: true
      };
    }

    return null;

  }

  register(): void {

    if (this.registerForm.invalid) {

      this.registerForm.markAllAsTouched();

      return;

    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';
    this.cdr.markForCheck();

    const formValue = this.registerForm.value;
    const email = String(formValue.email);
    const username = this.buildUsername(email);
    const selectedRole = String(formValue.role);

    this.authService.register({
      username,
      full_name: String(formValue.fullName),
      email,
      password: String(formValue.password),
      role_id: this.roleIds[selectedRole] ?? 2
    }).subscribe({
      next: () => {
        this.loading = false;
        this.successMessage = 'Registration successful. You can now log in.';
        this.cdr.markForCheck();
        this.router.navigate(['/login']);
      },
      error: (error: HttpErrorResponse) => {
        this.loading = false;
        this.errorMessage = this.extractErrorMessage(
          error,
          'Registration failed. Please check your details and try again.'
        );
        this.cdr.markForCheck();
      }
    });

  }

  private buildUsername(email: string): string {
    const raw = email
      .split('@')[0]
      .replace(/[^a-zA-Z0-9._-]/g, '');
    const valid = raw.length >= 3 ? raw : (raw + 'user').slice(0, 50);
    return valid.slice(0, 50);
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
