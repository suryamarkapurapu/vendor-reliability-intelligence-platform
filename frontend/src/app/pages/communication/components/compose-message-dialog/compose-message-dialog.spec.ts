import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComposeMessageDialog } from './compose-message-dialog';

describe('ComposeMessageDialog', () => {
  let component: ComposeMessageDialog;
  let fixture: ComponentFixture<ComposeMessageDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComposeMessageDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(ComposeMessageDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
