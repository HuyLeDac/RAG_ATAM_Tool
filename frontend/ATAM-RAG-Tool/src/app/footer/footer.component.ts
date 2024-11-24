import { Component, OnInit } from '@angular/core';
import { SharedDataService } from '../shared/shared-data.service'; // Import the SharedDataService
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule], // Add CommonModule to the imports array
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss']
})
export class FooterComponent implements OnInit {
  results: any; // Variable to store the results

  // Inject SharedDataService into the constructor
  constructor(private sharedDataService: SharedDataService) {}

  ngOnInit(): void {
    // Subscribe to the currentResults observable from the SharedDataService
    this.sharedDataService.currentResults.subscribe(results => {
      this.results = results;  // Update the results when they change
      console.log('Footer received updated results:', this.results);
    });
  }
}
