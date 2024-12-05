import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatIcon, MatIconModule } from '@angular/material/icon'; // <-- Add this import
import { MatDialogModule } from '@angular/material/dialog'; // <-- If you haven't already

@Component({
  selector: 'app-url-list',
  imports: [CommonModule, MatIconModule, MatDialogModule], // <-- Add MatIconModule and MatDialogModule to the imports array
  templateUrl: './url-list-dialog.component.html',
  styleUrls: ['./url-list-dialog.component.scss']
})
export class UrlListDialogComponent {
  urls: string[] = [];

  constructor(
    private http: HttpClient,
    public dialogRef: MatDialogRef<UrlListDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit(): void {
    this.getUrls();
  }

  // Fetches URLs from the backend
  getUrls(): void {
    const apiUrl = 'http://127.0.0.1:5000/get-urls'; // Replace with the actual backend URL

    this.http.get<any>(apiUrl).subscribe(
      (response) => {
        if (response.urls) {
          this.urls = response.urls;
        } else {
          console.error('No URLs found.');
        }
      },
      (error) => {
        console.error('Error fetching URLs:', error);
      }
    );
  }

  // Deletes a URL at the specified index
  deleteUrl(index: number): void {
    const urlToDelete = this.urls[index];
    const confirmDelete = confirm(`Are you sure you want to delete this URL: ${urlToDelete}?`);

    if (confirmDelete) {
      // Remove the URL from the list
      this.urls.splice(index, 1);

      // Optional: Call the backend to update the file after deleting
      this.updateUrlsOnBackend();
    }
  }

  // Updates the URLs list on the backend after a deletion
  updateUrlsOnBackend(): void {
    const apiUrl = 'http://127.0.0.1:5000/update-urls'; // Replace with the actual backend URL

    this.http.post<any>(apiUrl, { urls: this.urls }).subscribe(
      (response) => {
        console.log('URLs updated successfully', response);
      },
      (error) => {
        console.error('Error updating URLs on the backend:', error);
      }
    );
  }

  onClose(): void {
    this.dialogRef.close();
  }
}
