import { Component, EventEmitter, Output, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog } from '@angular/material/dialog';
import { ComposeMessageDialog } from '../compose-message-dialog/compose-message-dialog';
import { CommunicationService } from '../../../../services/communication.service';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-communication-header',
  standalone: true,
  imports: [
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './communication-header.html',
  styleUrl: './communication-header.css'
})
export class CommunicationHeader {
  @Output() messageSent = new EventEmitter<void>();

  private dialog = inject(MatDialog);
  private communicationService = inject(CommunicationService);
  private authService = inject(AuthService);

  composeMessage() {
    const dialogRef = this.dialog.open(ComposeMessageDialog, {
      width: '700px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && result.message) {
        this.authService.getMe().subscribe({
          next: (me) => {
            const receiverId = result.linked_user_id || me.user_id;
            const payload = {
              receiver_id: receiverId,
              vendor_id: result.vendor || result.vendor_id || undefined,
              subject: result.subject || 'Vendor Communication',
              message_body: result.message
            };

            this.communicationService.sendMessage(payload).subscribe({
              next: () => this.messageSent.emit(),
              error: (err) => console.error('Error sending message:', err)
            });
          },
          error: () => {
            // Fallback if getMe fails
            const payload = {
              receiver_id: result.linked_user_id || result.vendor || undefined,
              vendor_id: result.vendor || result.vendor_id || undefined,
              subject: result.subject || 'Vendor Communication',
              message_body: result.message
            };
            this.communicationService.sendMessage(payload).subscribe({
              next: () => this.messageSent.emit(),
              error: (err) => console.error('Error sending message:', err)
            });
          }
        });
      }
    });
  }
}