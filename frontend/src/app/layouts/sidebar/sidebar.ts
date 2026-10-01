import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    MatListModule,
    MatIconModule,
    RouterModule
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css'
})
export class Sidebar implements OnInit {

  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  userRole = '';

  ngOnInit(): void {
    this.authService.getMe().subscribe({
      next: (user) => {
        this.userRole = this.normalizeRole(user.role_name);
        this.cdr.markForCheck();
      },
      error: () => {
        this.userRole = '';
        this.cdr.markForCheck();
      }
    });
  }

  private normalizeRole(role: string | null | undefined): string {
    return String(role || '')
      .trim()
      .toUpperCase()
      .replace(/ /g, '_');
  }

  hasRole(roles: string[]): boolean {
    return roles
      .map(role => this.normalizeRole(role))
      .includes(this.userRole);
  }

  onLogout(event: Event): void {
    event.preventDefault();
    this.authService.logout();
  }
}