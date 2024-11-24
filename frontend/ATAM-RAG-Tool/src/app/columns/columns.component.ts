import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http'; 
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common'; // Import CommonModule
import { SharedDataService } from '../shared/shared-data.service'; // Import the SharedDataService


@Component({
  selector: 'app-columns',
  standalone: true,
  imports: [HttpClientModule, FormsModule, CommonModule], // Add CommonModule
  templateUrl: './columns.component.html',
  styleUrls: ['./columns.component.scss']
})

export class ColumnsComponent implements OnInit {

  results: any; // To store fetched results

  architecture_context: any;
  architectural_approaches: any;
  quality_criteria: any;
  scenarios: any;
  inputsUploaded = false; // Flag to track if inputs have been uploaded

  constructor(private http: HttpClient, private sharedDataService: SharedDataService) {}

  ngOnInit() {
    // Initialization logic
  }

  uploadInputs() {
    // Ensure all fields have values
    if (
      !this.architecture_context?.trim() ||
      !this.architectural_approaches?.trim() ||
      !this.quality_criteria?.trim() ||
      !this.scenarios?.trim()
    ) {
      alert('Please fill in all text fields.');
      return;
    }

    // Ensure all fields contain valid JSON
    let contextJson, approachesJson, criteriaJson, scenariosJson;
    try {
      contextJson = JSON.parse(this.architecture_context);
      approachesJson = JSON.parse(this.architectural_approaches);
      criteriaJson = JSON.parse(this.quality_criteria);
      scenariosJson = JSON.parse(this.scenarios);
    } catch (error) {
      alert('Please ensure all text fields contain valid JSON.');
      return;
    }

    // Prepare the JSON object to send to the backend
    const requestBody = {
      architecture_context: contextJson,
      architectural_approaches: approachesJson,
      quality_criteria: criteriaJson,
      scenarios: scenariosJson
    };

    // Send the JSON object to the backend using POST
    this.http.post('http://127.0.0.1:5000/upload-inputs', requestBody)
      .subscribe(
        response => {
          console.log('Analysis started successfully:', response);
          alert('Analysis process started successfully!');
          this.inputsUploaded = true; // Mark inputs as uploaded
        },
        error => {
          console.error('Error during HTTP request:', error);
          alert('An error occurred while starting the analysis process.');
        }
      );
  }

  fetchResults() {
    if (!this.inputsUploaded) {
      alert('Please upload inputs first by pressing "Add input" before fetching results.');
      return;
    }

    this.http.get('http://127.0.0.1:5000/get-results')
      .subscribe(
        (response: any) => {
          console.log('Results fetched successfully:', response);
          this.results = response; 
          this.sharedDataService.updateResults(this.results); // Share results with other components
        },
        error => {
          console.error('Error fetching results:', error);
          alert('An error occurred while fetching the results.');
        }
      );
  }
}
