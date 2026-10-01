import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditVendorDialog } from './edit-vendor-dialog';

describe('EditVendorDialog', () => {
  let component: EditVendorDialog;
  let fixture: ComponentFixture<EditVendorDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditVendorDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(EditVendorDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
