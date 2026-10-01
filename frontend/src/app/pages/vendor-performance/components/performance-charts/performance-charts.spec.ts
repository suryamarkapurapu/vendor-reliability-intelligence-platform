import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PerformanceCharts } from './performance-charts';

describe('PerformanceCharts', () => {
  let component: PerformanceCharts;
  let fixture: ComponentFixture<PerformanceCharts>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PerformanceCharts],
    }).compileComponents();

    fixture = TestBed.createComponent(PerformanceCharts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
