import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementChart } from './procurement-chart';

describe('ProcurementChart', () => {
  let component: ProcurementChart;
  let fixture: ComponentFixture<ProcurementChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementChart],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementChart);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
