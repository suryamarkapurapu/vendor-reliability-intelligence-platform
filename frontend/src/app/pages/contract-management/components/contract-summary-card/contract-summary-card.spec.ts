import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractSummaryCard } from './contract-summary-card';

describe('ContractSummaryCard', () => {
  let component: ContractSummaryCard;
  let fixture: ComponentFixture<ContractSummaryCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContractSummaryCard],
    }).compileComponents();

    fixture = TestBed.createComponent(ContractSummaryCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
