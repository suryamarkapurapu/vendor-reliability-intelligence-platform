import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorSummaryCard } from './vendor-summary-card';

describe('VendorSummaryCard', () => {
  let component: VendorSummaryCard;
  let fixture: ComponentFixture<VendorSummaryCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorSummaryCard],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorSummaryCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
