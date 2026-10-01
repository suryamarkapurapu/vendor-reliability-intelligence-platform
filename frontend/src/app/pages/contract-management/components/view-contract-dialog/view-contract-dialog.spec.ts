import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewContractDialog } from './view-contract-dialog';

describe('ViewContractDialog', () => {
  let component: ViewContractDialog;
  let fixture: ComponentFixture<ViewContractDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewContractDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(ViewContractDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
