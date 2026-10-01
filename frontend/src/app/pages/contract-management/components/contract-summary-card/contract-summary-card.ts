import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
selector:'app-contract-summary-card',
standalone:true,
imports:[
MatCardModule,
MatIconModule
],
templateUrl:'./contract-summary-card.html',
styleUrl:'./contract-summary-card.css'
})
export class ContractSummaryCard{

@Input() title='';

@Input() value=0;

@Input() icon = '';

}