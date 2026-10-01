import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommunicationSummaryCard } from './communication-summary-card';

describe('CommunicationSummaryCard', () => {
  let component: CommunicationSummaryCard;
  let fixture: ComponentFixture<CommunicationSummaryCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommunicationSummaryCard],
    }).compileComponents();

    fixture = TestBed.createComponent(CommunicationSummaryCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
