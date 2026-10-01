import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommunicationTable } from './communication-table';

describe('CommunicationTable', () => {
  let component: CommunicationTable;
  let fixture: ComponentFixture<CommunicationTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommunicationTable],
    }).compileComponents();

    fixture = TestBed.createComponent(CommunicationTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
