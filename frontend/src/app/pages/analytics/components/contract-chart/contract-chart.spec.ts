import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractChart } from './contract-chart';

describe('ContractChart', () => {
  let component: ContractChart;
  let fixture: ComponentFixture<ContractChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContractChart],
    }).compileComponents();

    fixture = TestBed.createComponent(ContractChart);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
