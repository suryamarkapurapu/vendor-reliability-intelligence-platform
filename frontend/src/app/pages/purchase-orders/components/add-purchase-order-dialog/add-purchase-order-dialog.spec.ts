import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddPurchaseOrderDialog } from './add-purchase-order-dialog';

describe('AddPurchaseOrderDialog', () => {
  let component: AddPurchaseOrderDialog;
  let fixture: ComponentFixture<AddPurchaseOrderDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddPurchaseOrderDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(AddPurchaseOrderDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
