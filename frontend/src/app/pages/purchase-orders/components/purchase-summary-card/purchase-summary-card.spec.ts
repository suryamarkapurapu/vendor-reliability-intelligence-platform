import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PurchaseSummaryCard } from './purchase-summary-card';

describe('PurchaseSummaryCard', () => {
  let component: PurchaseSummaryCard;
  let fixture: ComponentFixture<PurchaseSummaryCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PurchaseSummaryCard],
    }).compileComponents();

    fixture = TestBed.createComponent(PurchaseSummaryCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
