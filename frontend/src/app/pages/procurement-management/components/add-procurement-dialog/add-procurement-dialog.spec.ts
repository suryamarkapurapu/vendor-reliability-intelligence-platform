import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddProcurementDialog } from './add-procurement-dialog';

describe('AddProcurementDialog', () => {
  let component: AddProcurementDialog;
  let fixture: ComponentFixture<AddProcurementDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddProcurementDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(AddProcurementDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
