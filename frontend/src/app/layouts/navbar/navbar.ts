import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { VrBrand } from '../../shared/components/vr-brand/vr-brand';

import { AuthService } from '../../services/auth.service';
import {
  NotificationService,
  Notification
} from '../../services/notification.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule,
    VrBrand
  ],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar implements OnInit {

  username = '';
  roleName = '';

  notifications: Notification[] = [];
  unreadCount = 0;

  constructor(
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadUser();
    this.loadNotifications();
  }

  private loadUser(): void {
    this.authService.getMe().subscribe({
      next: (user) => {
        this.username = user.username;
        this.roleName = user.role_name ?? '';
      },
      error: (error) => {
        console.error('Failed to load logged-in user:', error);
      }
    });
  }

  private loadNotifications(): void {
    this.notificationService.getNotifications().subscribe({
      next: (notifications) => {
        this.notifications = notifications;
      },
      error: (error) => {
        console.error('Failed to load notifications:', error);
      }
    });

    this.notificationService.getUnreadCount().subscribe({
      next: (result) => {
        this.unreadCount = result.count;
      },
      error: (error) => {
        console.error('Failed to load unread notification count:', error);
      }
    });
  }

  markAsRead(notification: Notification): void {

    if (notification.is_read) {
      return;
    }

    this.notificationService
      .markAsRead(notification.notification_id)
      .subscribe({
        next: (updatedNotification) => {

          notification.is_read = updatedNotification.is_read;

          if (this.unreadCount > 0) {
            this.unreadCount--;
          }
        },
        error: (error) => {
          console.error('Failed to mark notification as read:', error);
        }
      });
  }
}