import { Component } from '@angular/core';

import { ReactiveFormsModule, FormBuilder } from '@angular/forms';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-reports-toolbar',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule
  ],
  templateUrl: './reports-toolbar.html',
  styleUrl: './reports-toolbar.css'
})
export class ReportsToolbar {

  toolbarForm;

  constructor(private fb: FormBuilder){

    this.toolbarForm = this.fb.group({

      search:[''],

      category:['All'],

      status:['All']

    });

  }

}