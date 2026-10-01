import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementTable } from './procurement-table';

describe('ProcurementTable', () => {
  let component: ProcurementTable;
  let fixture: ComponentFixture<ProcurementTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementTable],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
