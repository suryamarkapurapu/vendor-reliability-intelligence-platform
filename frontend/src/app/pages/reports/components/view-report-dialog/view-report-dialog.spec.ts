import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewReportDialog } from './view-report-dialog';

describe('ViewReportDialog', () => {
  let component: ViewReportDialog;
  let fixture: ComponentFixture<ViewReportDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewReportDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(ViewReportDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
