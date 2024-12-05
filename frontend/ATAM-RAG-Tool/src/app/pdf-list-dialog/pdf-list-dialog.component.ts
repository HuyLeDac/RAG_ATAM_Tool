import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pdf-list-dialog',
  standalone: true,
  imports: [MatProgressSpinnerModule, CommonModule],
  templateUrl: './pdf-list-dialog.component.html',
  styleUrls: ['./pdf-list-dialog.component.scss']
})
export class PdfListDialogComponent implements OnInit {

  pdfFiles: string[] = []; // List of PDF files
  loading = true; // Loading state
  backendUrl = 'http://127.0.0.1:5000'; // Backend URL

  constructor(
    private dialogRef: MatDialogRef<PdfListDialogComponent>,
    private http: HttpClient,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit(): void {
    // Fetch the list of PDFs from the backend
    this.http.get<any>(`${this.backendUrl}/list-pdfs`).subscribe(
      (response) => {
        this.pdfFiles = response.pdf_files || [];
        this.loading = false;
      },
      (error) => {
        console.error('Error fetching PDF files:', error);
        this.loading = false;
      }
    );
  }

  downloadPdf(pdf: string): void {
    window.open(`${this.backendUrl}/download/${pdf}`, '_blank');
  }

  deletePdf(pdfName: string): void {
    if (confirm(`Are you sure you want to delete the PDF '${pdfName}'?`)) {
      this.http.post(`${this.backendUrl}/delete-pdf/${pdfName}`, {}).subscribe(
        (response: any) => {
          // Successfully deleted, now update the list of PDFs
          this.pdfFiles = response.updated_pdf_files || [];
          console.log(`PDF '${pdfName}' deleted successfully.`);
          alert(`PDF '${pdfName}' deleted successfully.`);
        },
        (error) => {
          console.error('Error deleting PDF:', error);
          alert(`Error deleting PDF '${pdfName}'`);
        }
      );
    }
    
    // reload the list of PDFs
    this.http.get<any>(`${this.backendUrl}/list-pdfs`).subscribe(
      (response) => {
        this.pdfFiles = response.pdf_files || [];
      },
      (error) => {
        console.error('Error fetching PDF files:', error);
      }
    );
  }

  closeDialog(): void {
    this.dialogRef.close();
  }
}
