import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorTable } from './vendor-table';

describe('VendorTable', () => {
  let component: VendorTable;
  let fixture: ComponentFixture<VendorTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorTable],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
