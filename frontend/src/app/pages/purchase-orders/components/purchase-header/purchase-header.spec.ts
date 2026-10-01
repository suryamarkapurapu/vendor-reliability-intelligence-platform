import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PurchaseHeader } from './purchase-header';

describe('PurchaseHeader', () => {
  let component: PurchaseHeader;
  let fixture: ComponentFixture<PurchaseHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PurchaseHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(PurchaseHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
