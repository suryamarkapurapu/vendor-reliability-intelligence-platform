import { Component, EventEmitter, Output } from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-vendor-toolbar',
  standalone: true,
  imports: [
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    FormsModule
  ],
  templateUrl: './vendor-toolbar.html',
  styleUrl: './vendor-toolbar.css'
})
export class VendorToolbar {

  searchText = '';
  selectedCategory = 'All';
  selectedStatus = 'All';

  @Output() searchChange = new EventEmitter<string>();
  @Output() categoryChange = new EventEmitter<string>();
  @Output() statusChange = new EventEmitter<string>();

  onSearch() {
    this.searchChange.emit(this.searchText);
  }

  onCategoryChange(category: string) {
    this.selectedCategory = category;
    this.categoryChange.emit(this.selectedCategory);
  }

  onStatusChange(status: string) {
    this.selectedStatus = status;
    this.statusChange.emit(this.selectedStatus);
  }

}
