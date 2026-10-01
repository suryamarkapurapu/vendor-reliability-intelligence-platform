import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';

import {
  ActivityLog,
  ActivityLogService
} from '../../../../services/activity-log.service';

@Component({
  selector: 'app-recent-activity',
  standalone: true,
  imports: [
    MatCardModule,
    MatListModule,
    MatIconModule
  ],
  templateUrl: './recent-activity.html',
  styleUrl: './recent-activity.css'
})
export class RecentActivity implements OnInit {

  private activityLogService = inject(ActivityLogService);
  private cdr = inject(ChangeDetectorRef);

  activities: ActivityLog[] = [];

  ngOnInit(): void {

    this.activityLogService.getRecentActivity(10).subscribe({

      next: (response) => {

        this.activities = response;

        this.cdr.markForCheck();
      },

      error: (error) => {

        console.error(
          'Failed to load recent activity:',
          error
        );

        this.activities = [];

        this.cdr.markForCheck();
      }

    });
  }
}