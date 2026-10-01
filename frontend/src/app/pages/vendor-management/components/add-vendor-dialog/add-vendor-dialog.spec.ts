import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddVendorDialog } from './add-vendor-dialog';

describe('AddVendorDialog', () => {
  let component: AddVendorDialog;
  let fixture: ComponentFixture<AddVendorDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddVendorDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(AddVendorDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
