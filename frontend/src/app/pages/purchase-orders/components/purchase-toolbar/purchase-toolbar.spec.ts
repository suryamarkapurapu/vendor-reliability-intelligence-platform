import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PurchaseToolbar } from './purchase-toolbar';

describe('PurchaseToolbar', () => {
  let component: PurchaseToolbar;
  let fixture: ComponentFixture<PurchaseToolbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PurchaseToolbar],
    }).compileComponents();

    fixture = TestBed.createComponent(PurchaseToolbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
