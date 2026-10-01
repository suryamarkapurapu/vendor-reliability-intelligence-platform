import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractHeader } from './contract-header';

describe('ContractHeader', () => {
  let component: ContractHeader;
  let fixture: ComponentFixture<ContractHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContractHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(ContractHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
