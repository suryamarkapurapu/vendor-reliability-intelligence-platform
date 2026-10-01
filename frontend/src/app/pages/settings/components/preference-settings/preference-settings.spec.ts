import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PreferenceSettings } from './preference-settings';

describe('PreferenceSettings', () => {
  let component: PreferenceSettings;
  let fixture: ComponentFixture<PreferenceSettings>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PreferenceSettings],
    }).compileComponents();

    fixture = TestBed.createComponent(PreferenceSettings);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
