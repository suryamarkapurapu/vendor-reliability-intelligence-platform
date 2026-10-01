import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorChart } from './vendor-chart';

describe('VendorChart', () => {
  let component: VendorChart;
  let fixture: ComponentFixture<VendorChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorChart],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorChart);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
