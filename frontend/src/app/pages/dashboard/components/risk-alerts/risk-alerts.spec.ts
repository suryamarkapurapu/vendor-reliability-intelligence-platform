import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RiskAlerts } from './risk-alerts';

describe('RiskAlerts', () => {
  let component: RiskAlerts;
  let fixture: ComponentFixture<RiskAlerts>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RiskAlerts],
    }).compileComponents();

    fixture = TestBed.createComponent(RiskAlerts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
