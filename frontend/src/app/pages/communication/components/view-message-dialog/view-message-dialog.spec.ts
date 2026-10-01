import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewMessageDialog } from './view-message-dialog';

describe('ViewMessageDialog', () => {
  let component: ViewMessageDialog;
  let fixture: ComponentFixture<ViewMessageDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewMessageDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(ViewMessageDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
