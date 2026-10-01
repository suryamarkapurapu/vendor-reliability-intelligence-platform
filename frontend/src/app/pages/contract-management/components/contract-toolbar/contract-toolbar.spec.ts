import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractToolbar } from './contract-toolbar';

describe('ContractToolbar', () => {
  let component: ContractToolbar;
  let fixture: ComponentFixture<ContractToolbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContractToolbar],
    }).compileComponents();

    fixture = TestBed.createComponent(ContractToolbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
