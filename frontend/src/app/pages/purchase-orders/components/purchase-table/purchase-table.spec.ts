import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PurchaseTable } from './purchase-table';

describe('PurchaseTable', () => {
  let component: PurchaseTable;
  let fixture: ComponentFixture<PurchaseTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PurchaseTable],
    }).compileComponents();

    fixture = TestBed.createComponent(PurchaseTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
