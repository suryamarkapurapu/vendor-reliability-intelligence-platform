import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalyticsSummaryCard } from './analytics-summary-card';

describe('AnalyticsSummaryCard', () => {
  let component: AnalyticsSummaryCard;
  let fixture: ComponentFixture<AnalyticsSummaryCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AnalyticsSummaryCard],
    }).compileComponents();

    fixture = TestBed.createComponent(AnalyticsSummaryCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
