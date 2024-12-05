import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PdfListDialogComponent } from './pdf-list-dialog.component';

describe('PdfListDialogComponent', () => {
  let component: PdfListDialogComponent;
  let fixture: ComponentFixture<PdfListDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PdfListDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PdfListDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
