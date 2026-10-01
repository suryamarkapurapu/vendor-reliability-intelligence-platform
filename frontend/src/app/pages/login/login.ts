import { Component, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  ReactiveFormsModule,
  FormBuilder,
  Validators
} from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';

import { Router } from '@angular/router';

import { AuthService } from '../../services/auth.service';
import { RouterLink } from '@angular/router';


@Component({
  selector: 'app-login',

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
    MatIconModule

  ],

  templateUrl: './login.html',

  styleUrl: './login.css'
})

export class Login {

  hidePassword = true;

  loading = false;

  errorMessage = '';


  loginForm;


  private cdr = inject(ChangeDetectorRef);

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService
  ) {

    this.loginForm = this.fb.group({
      email: [
        '',
        [
          Validators.required
        ]
      ],
      password: [
        '',
        Validators.required
      ],
      rememberMe: [false]
    });
  }

  login(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    const credentials = {
      username: (this.loginForm.value.email || '').trim(),
      password: this.loginForm.value.password || ''
    };

    this.authService.login(credentials).subscribe({
      next: (response) => {
        this.authService.saveToken(
          response.access_token,
          Boolean(this.loginForm.value.rememberMe)
        );

        this.loading = false;
        this.cdr.markForCheck();

        this.router.navigate([
          '/dashboard'
        ]);
      },

      error: (error) => {
        console.error(
          'Login failed:',
          error
        );

        this.loading = false;
        this.errorMessage =
          error.error?.detail || 'Invalid email or password';
        this.cdr.markForCheck();
      }
    });
  }
}