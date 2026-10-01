import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Notification {
  notification_id: string;
  user_id: string;
  channel: string;
  notification_type: string;
  title: string;
  message: string;
  related_entity_type?: string | null;
  related_entity_id?: string | null;
  priority: string;
  is_read: boolean;
  created_at: string;
}

export interface UnreadNotificationCount {
  count: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  private readonly apiUrl = 'http://127.0.0.1:8000/api/v1/notifications';

  constructor(private http: HttpClient) {}

  getNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(this.apiUrl);
  }

  getUnreadCount(): Observable<UnreadNotificationCount> {
    return this.http.get<UnreadNotificationCount>(
      `${this.apiUrl}/unread-count`
    );
  }

  markAsRead(notificationId: string): Observable<Notification> {
    return this.http.patch<Notification>(
      `${this.apiUrl}/${notificationId}/read`,
      {}
    );
  }
}