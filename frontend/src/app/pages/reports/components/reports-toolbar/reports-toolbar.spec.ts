import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReportsToolbar } from './reports-toolbar';

describe('ReportsToolbar', () => {
  let component: ReportsToolbar;
  let fixture: ComponentFixture<ReportsToolbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReportsToolbar],
    }).compileComponents();

    fixture = TestBed.createComponent(ReportsToolbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
