import { Component, EventEmitter, Output } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-settings-header',
  standalone: true,
  imports: [
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './settings-header.html',
  styleUrl: './settings-header.css'
})
export class SettingsHeader {

  @Output() save = new EventEmitter<void>();

  saveSettings(): void {
    this.save.emit();
  }

}
