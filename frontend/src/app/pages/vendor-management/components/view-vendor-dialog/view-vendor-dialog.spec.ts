import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewVendorDialog } from './view-vendor-dialog';

describe('ViewVendorDialog', () => {
  let component: ViewVendorDialog;
  let fixture: ComponentFixture<ViewVendorDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewVendorDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(ViewVendorDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
