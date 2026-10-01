import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorToolbar } from './vendor-toolbar';

describe('VendorToolbar', () => {
  let component: VendorToolbar;
  let fixture: ComponentFixture<VendorToolbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorToolbar],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorToolbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
