import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementToolbar } from './procurement-toolbar';

describe('ProcurementToolbar', () => {
  let component: ProcurementToolbar;
  let fixture: ComponentFixture<ProcurementToolbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementToolbar],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementToolbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
