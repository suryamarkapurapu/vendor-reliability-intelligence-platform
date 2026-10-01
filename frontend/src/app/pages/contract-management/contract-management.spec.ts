import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractManagement } from './contract-management';

describe('ContractManagement', () => {
  let component: ContractManagement;
  let fixture: ComponentFixture<ContractManagement>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContractManagement],
    }).compileComponents();

    fixture = TestBed.createComponent(ContractManagement);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
