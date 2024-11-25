import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms'; // For [(ngModel)]

@Component({
  selector: 'app-add-url-dialog',
  standalone: true,
  imports: [MatFormFieldModule, MatInputModule, FormsModule], // Import required modules
  template: `
    <h1 mat-dialog-title>Add URL</h1>
    <div mat-dialog-content>
      <mat-form-field style="width: 100%;">
        <mat-label>Enter URL</mat-label>
        <input matInput [(ngModel)]="url" placeholder="e.g., https://example.com" />
      </mat-form-field>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button (click)="close()">Cancel</button>
      <button mat-button color="primary" (click)="submit()">Add</button>
    </div>
  `,
  styles: [
    `
      mat-form-field {
        margin-top: 10px;
      }
    `,
  ],
})
export class AddUrlDialogComponent {
  url: string = '';

  constructor(
    public dialogRef: MatDialogRef<AddUrlDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  close(): void {
    this.dialogRef.close();
  }

  submit(): void {
    if (this.url.trim()) {
      this.dialogRef.close(this.url); // Pass the URL back to the parent component
    }
  }
}
