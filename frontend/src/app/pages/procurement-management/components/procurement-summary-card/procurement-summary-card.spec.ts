import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementSummaryCard } from './procurement-summary-card';

describe('ProcurementSummaryCard', () => {
  let component: ProcurementSummaryCard;
  let fixture: ComponentFixture<ProcurementSummaryCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementSummaryCard],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementSummaryCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
