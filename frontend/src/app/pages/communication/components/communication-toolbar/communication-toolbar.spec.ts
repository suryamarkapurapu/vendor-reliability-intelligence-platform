import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommunicationToolbar } from './communication-toolbar';

describe('CommunicationToolbar', () => {
  let component: CommunicationToolbar;
  let fixture: ComponentFixture<CommunicationToolbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommunicationToolbar],
    }).compileComponents();

    fixture = TestBed.createComponent(CommunicationToolbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
