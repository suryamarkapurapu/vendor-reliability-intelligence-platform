import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementHeader } from './procurement-header';

describe('ProcurementHeader', () => {
  let component: ProcurementHeader;
  let fixture: ComponentFixture<ProcurementHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
