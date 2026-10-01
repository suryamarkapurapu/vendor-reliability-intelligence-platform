import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';

export interface ActivityLog {
  log_id: number;
  user_id: string | null;
  entity_type: string;
  entity_id: string | null;
  action: string;
  description: string | null;
  ip_address: string | null;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class ActivityLogService {

  private http = inject(HttpClient);

  private apiUrl = API_BASE_URL;

  getRecentActivity(limit: number = 10): Observable<ActivityLog[]> {
    return this.http.get<ActivityLog[]>(
      `${this.apiUrl}/activity-logs/recent?limit=${limit}`
    );
  }
}