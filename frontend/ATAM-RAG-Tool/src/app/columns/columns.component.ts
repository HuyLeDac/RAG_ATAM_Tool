import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http'; 
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common'; // Import CommonModule
import { SharedDataService } from '../shared/shared-data.service'; // Import the SharedDataService
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { AddUrlDialogComponent } from '../add-url-dialog/add-url-dialog.component';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { LoadingDialogComponent } from '../loading-dialog/loading-dialog.component';


@Component({
  selector: 'app-columns',
  standalone: true,
  imports: [HttpClientModule, 
            FormsModule, 
            CommonModule, 
            MatDialogModule, 
            AddUrlDialogComponent, 
            MatProgressSpinnerModule, 
            LoadingDialogComponent], // Add CommonModule
  templateUrl: './columns.component.html',
  styleUrls: ['./columns.component.scss']
})

export class ColumnsComponent implements OnInit {

  results: any; // To store fetched results

  architecture_context: any = { "architectureDescription": {}}; // Initialize as an empty object
  architectural_approaches: any;
  quality_criteria: any;
  scenarios: any = '';

  systemPurpose: string = '';
  systemConstraint: string = '';
  systemInteraction: string = '';

  scenarioName: string = '';
  scenarioAttribute: string = '';
  scenarioEnvironment: string = '';
  scenarioStimulus: string = '';
  scenarioResponse: string = '';

  inputsUploaded = false; // Flag to track if inputs have been uploaded
  loading = false; // New loading state

  constructor(private http: HttpClient, private sharedDataService: SharedDataService, private dialog: MatDialog) {}

  ngOnInit() {
    // Initialization logic
  }

  addURL() {
    const dialogRef = this.dialog.open(AddUrlDialogComponent);
  
    dialogRef.afterClosed().subscribe((url) => {
      if (url && this.isValidUrl(url)) {
        // Send the URL to the backend
        this.http.post('http://127.0.0.1:5000/upload-url', { url }).subscribe(
          (response) => {
            console.log('URL uploaded successfully:', response);
            alert('URL uploaded successfully!');
          },
          (error) => {
            console.error('Error uploading URL:', error);
            alert('An error occurred while uploading the URL.');
          }
        );
      } else if (url) {
        alert('Invalid URL format. Please enter a valid URL.');
      }
    });
  }
  

  isValidUrl(url: string): boolean {
    const urlPattern = new RegExp(
      '^(https?:\\/\\/)?' + // protocol
      '((([a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,})|' + // domain name
      'localhost|' + // or localhost
      '\\d{1,3}(\\.\\d{1,3}){3})' + // or IP address
      '(\\:\\d+)?(\\/[-a-zA-Z0-9@:%._\\+~#=]*)*' + // port and path
      '(\\?[;&a-zA-Z0-9%_.~+=-]*)?' + // query string
      '(\\#[-a-zA-Z0-9_]*)?$', // fragment locator
      'i'
    );
    return !!urlPattern.test(url);
  }
  

  addPdf(event: Event) {
    const input = event.target as HTMLInputElement;
  
    if (input.files) {
      const formData = new FormData();
  
      // Append selected files to the FormData object
      Array.from(input.files).forEach((file) => {
        formData.append('pdf', file);
      });
  
      // Send the FormData object to the backend
      this.http.post('http://127.0.0.1:5000/upload-pdf', formData).subscribe(
        (response) => {
          console.log('PDFs uploaded successfully:', response);
          alert('PDFs uploaded successfully!');
        },
        (error) => {
          console.error('Error uploading PDFs:', error);
          alert('An error occurred while uploading the PDFs.');
        }
      );
    }
  }
  
  // Trigger file upload dialog
  triggerPdfUpload() {
    const fileInput = document.getElementById('pdfUpload') as HTMLInputElement;
    if (fileInput) fileInput.click();
  }
  

  addSystemPurpose() {
    if (this.systemPurpose.trim()) {
      this.architecture_context["architectureDescription"]['systemPurpose'] = this.systemPurpose.trim();
      this.systemPurpose = ''; // Clear the input field
      alert('System purpose added successfully!');
    } else {
      alert('Please enter a valid system purpose.');
    }
  }

  addConstraint() {
    if (this.systemConstraint.trim()) {
      if (!this.architecture_context["architectureDescription"]['technicalConstraints']) {
        this.architecture_context["architectureDescription"]['technicalConstraints'] = [];
      }
      this.architecture_context["architectureDescription"]['technicalConstraints'].push(this.systemConstraint.trim());
      this.systemConstraint = ''; // Clear the input field
      alert('System constraint added successfully!');
    } else {
      alert('Please enter a valid system constraint.');
    }
  }

  addInteraction() {
    if (this.systemInteraction.trim()) {
      if (!this.architecture_context["architectureDescription"]['systemInteractions']) {
        this.architecture_context["architectureDescription"]['systemInteractions'] = [];
      }
      this.architecture_context["architectureDescription"]['systemInteractions'].push(this.systemInteraction.trim());
      this.systemInteraction = ''; // Clear the input field
      alert('System interaction added successfully!');
    } else {
      alert('Please enter a valid system interaction.');
    }
  }

  uploadInputs() {
    // Ensure all fields have values
    if (
      Object.keys(this.architecture_context).length === 0 ||
      !this.architectural_approaches?.trim() ||
      !this.quality_criteria?.trim() ||
      !this.scenarios.trim()
    ) {
      alert('Please fill in all required fields.');
      return;
    }

    // Ensure all fields contain valid JSON
    let approachesJson, criteriaJson, scenariosJson;
    try {
      approachesJson = JSON.parse(this.architectural_approaches);
      criteriaJson = JSON.parse(this.quality_criteria);
      scenariosJson = JSON.parse(this.scenarios);
    } catch (error) {
      alert('Please ensure all text fields contain valid JSON.');
      return;
    }

    // Prepare the JSON object to send to the backend
    const requestBody = {
      architecture_context: this.architecture_context,
      architectural_approaches: approachesJson,
      quality_criteria: criteriaJson,
      scenarios: scenariosJson,
    };

    // Send the JSON object to the backend using POST
    this.http.post('http://127.0.0.1:5000/upload-inputs', requestBody).subscribe(
      (response) => {
        console.log('Input uploaded successfully:', response);
        alert('Input uploaded successfully!');
        this.inputsUploaded = true; // Mark inputs as uploaded
      },
      (error) => {
        console.error('Error during HTTP request:', error);
        alert('An error occurred while starting the analysis process.');
      }
    );
  }

  reset() {
    this.results = null;
    this.sharedDataService.updateResults(this.results);
    this.architecture_context = {"architectureDescription": {}};
    this.architectural_approaches = '';
    this.quality_criteria = '';
    this.scenarios = '';
    this.inputsUploaded = false;

    this.systemPurpose = '';
    this.systemConstraint = '';
    this.systemInteraction = '';
  }

  fetchResults() {
    if (!this.inputsUploaded) {
      alert('Please upload inputs first by pressing "Upload input" before fetching results.');
      return;
    }
  
    const dialogRef = this.dialog.open(LoadingDialogComponent, {
      disableClose: true, // Prevent closing the dialog manually
    });
  
    this.http.get('http://127.0.0.1:5000/get-results').subscribe(
      (response: any) => {
        console.log('Results fetched successfully:', response);
        alert('Results fetched successfully!');
        this.results = response;
        this.sharedDataService.updateResults(this.results);
        dialogRef.close(); // Close the loading dialog
      },
      (error) => {
        console.error('Error fetching results:', error);
        alert('An error occurred while fetching the results.');
        dialogRef.close(); // Close the loading dialog
      }
    );
  }

  fetchResultsWithoutQuery() {
    if (!this.inputsUploaded) {
      alert('Please upload inputs first by pressing "Add input" before fetching results.');
      return;
    }
  
    const dialogRef = this.dialog.open(LoadingDialogComponent, {
      disableClose: true, // Prevent closing the dialog manually
    });
  
    this.http.get('http://127.0.0.1:5000/get-results-without-retrieval').subscribe(
      (response: any) => {
        console.log('Results fetched successfully:', response);
        alert('Results fetched successfully!');
        this.results = response;
        this.sharedDataService.updateResults(this.results);
        dialogRef.close(); // Close the loading dialog
      },
      (error) => {
        console.error('Error fetching results:', error);
        alert('An error occurred while fetching the results.');
        dialogRef.close(); // Close the loading dialog
      }
    );
  }

  addScenario() {
    if (
      !this.scenarioName.trim() ||
      !this.scenarioAttribute.trim() ||
      !this.scenarioEnvironment.trim() ||
      !this.scenarioStimulus.trim() ||
      !this.scenarioResponse.trim()
    ) {
      alert('Please fill out all fields before adding a scenario.');
      return;
    }
  
    // Parse the existing scenarios or initialize an empty array
    if (!this.scenarios.trim()) {
      this.scenarios = '{"scenarios": []}';
    }
  
    let scenariosJson;
    try {
      scenariosJson = JSON.parse(this.scenarios); // Parse existing JSON
    } catch (error) {
      console.error('Error parsing scenarios:', error);
      alert('Invalid scenarios format. Resetting.');
      this.scenarios = '{"scenarios": []}';
      scenariosJson = { scenarios: [] };
    }
  
    // Create the new scenario
    const newScenario = {
      scenario: this.scenarioName.trim(),
      attribute: this.scenarioAttribute.trim(),
      environment: this.scenarioEnvironment.trim(),
      stimulus: this.scenarioStimulus.trim(),
      response: this.scenarioResponse.trim()
    };
  
    // Add the new scenario to the array
    scenariosJson.scenarios.push(newScenario);
  
    // Update the scenarios field as a JSON string
    this.scenarios = JSON.stringify(scenariosJson, null, 2); // Format with 2-space indentation for readability
  
    // Clear the input fields
    this.scenarioName = '';
    this.scenarioAttribute = '';
    this.scenarioEnvironment = '';
    this.scenarioStimulus = '';
    this.scenarioResponse = '';
  
    alert('Scenario added successfully!');
  }

  get formattedScenarios(): string {
    try {
      return JSON.stringify(JSON.parse(this.scenarios || '{}'), null, 2); // Beautify JSON
    } catch (error) {
      return 'Invalid JSON'; // Handle invalid JSON case
    }
  }  
  

}
