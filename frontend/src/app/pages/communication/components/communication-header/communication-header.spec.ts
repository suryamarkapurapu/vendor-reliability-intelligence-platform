import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommunicationHeader } from './communication-header';

describe('CommunicationHeader', () => {
  let component: CommunicationHeader;
  let fixture: ComponentFixture<CommunicationHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommunicationHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(CommunicationHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
