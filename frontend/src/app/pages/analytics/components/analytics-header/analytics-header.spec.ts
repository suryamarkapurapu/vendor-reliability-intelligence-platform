import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalyticsHeader } from './analytics-header';

describe('AnalyticsHeader', () => {
  let component: AnalyticsHeader;
  let fixture: ComponentFixture<AnalyticsHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AnalyticsHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(AnalyticsHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
