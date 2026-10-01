import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-procurement-toolbar',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule
  ],
  templateUrl: './procurement-toolbar.html',
  styleUrl: './procurement-toolbar.css'
})
export class ProcurementToolbar {

  searchText = '';

  selectedStatus = '';

  selectedPriority = '';

}