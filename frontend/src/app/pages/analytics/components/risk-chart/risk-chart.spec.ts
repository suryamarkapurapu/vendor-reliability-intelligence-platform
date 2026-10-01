import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RiskChart } from './risk-chart';

describe('RiskChart', () => {
  let component: RiskChart;
  let fixture: ComponentFixture<RiskChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RiskChart],
    }).compileComponents();

    fixture = TestBed.createComponent(RiskChart);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
