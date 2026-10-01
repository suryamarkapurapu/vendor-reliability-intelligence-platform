import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddContractDialog } from './add-contract-dialog';

describe('AddContractDialog', () => {
  let component: AddContractDialog;
  let fixture: ComponentFixture<AddContractDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddContractDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(AddContractDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
