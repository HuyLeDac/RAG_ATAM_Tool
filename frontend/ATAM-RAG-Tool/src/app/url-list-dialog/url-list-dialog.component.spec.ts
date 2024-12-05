import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UrlListDialogComponent } from './url-list-dialog.component';

describe('UrlListDialogComponent', () => {
  let component: UrlListDialogComponent;
  let fixture: ComponentFixture<UrlListDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UrlListDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UrlListDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
