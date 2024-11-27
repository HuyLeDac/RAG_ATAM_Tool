import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms'; // For [(ngModel)]

@Component({
  selector: 'app-add-url-dialog',
  standalone: true,
  imports: [MatFormFieldModule, MatInputModule, FormsModule], // Import required modules
  templateUrl: './add-url-dialog.component.html',
  styleUrls: ['./add-url-dialog.component.scss']
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
