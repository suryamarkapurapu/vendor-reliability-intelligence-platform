import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenerateReportDialog } from './generate-report-dialog';

describe('GenerateReportDialog', () => {
  let component: GenerateReportDialog;
  let fixture: ComponentFixture<GenerateReportDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GenerateReportDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(GenerateReportDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
