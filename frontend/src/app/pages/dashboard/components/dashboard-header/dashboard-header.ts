import { Component, OnInit, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-dashboard-header',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './dashboard-header.html',
  styleUrl: './dashboard-header.css'
})
export class DashboardHeader implements OnInit {

  private authService = inject(AuthService);

  currentDate = new Date();

  userName = 'User';
  userRole = '';

  ngOnInit(): void {
    this.authService.getMe().subscribe({
      next: (user) => {
        this.userName = user.full_name || 'User';
        this.userRole = user.role_name || '';
      },
      error: (error) => {
        console.error('Failed to load current user:', error);
      }
    });
  }
}