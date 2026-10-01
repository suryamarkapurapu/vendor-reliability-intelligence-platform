import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorHeader } from './vendor-header';


describe('VendorHeader', () => {
  let component: VendorHeader;
  let fixture: ComponentFixture<VendorHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
