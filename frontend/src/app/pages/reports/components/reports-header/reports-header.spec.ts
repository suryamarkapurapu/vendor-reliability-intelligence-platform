import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReportsHeader } from './reports-header';

describe('ReportsHeader', () => {
  let component: ReportsHeader;
  let fixture: ComponentFixture<ReportsHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReportsHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(ReportsHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
