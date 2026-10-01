import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteVendorDialog } from './delete-vendor-dialog';

describe('DeleteVendorDialog', () => {
  let component: DeleteVendorDialog;
  let fixture: ComponentFixture<DeleteVendorDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeleteVendorDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(DeleteVendorDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
