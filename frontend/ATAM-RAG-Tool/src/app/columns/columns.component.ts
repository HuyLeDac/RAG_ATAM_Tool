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
            MatProgressSpinnerModule,], 
  templateUrl: './columns.component.html',
  styleUrls: ['./columns.component.scss']
})

export class ColumnsComponent implements OnInit {

  results: any; // To store fetched results

  architecture_context: any = '{ "architectureDescription": {}}'; // Initialize as an empty object
  architectural_approaches: any = '{"architecturalApproaches": []}';
  quality_criteria: any = '{ "quality_criteria" : [] }';
  scenarios: any = '{ "scenarios" : [] }';

  systemPurpose: string = '';
  systemConstraint: string = '';
  systemInteraction: string = '';

  approach_name: string = '';
  approach_description: string = '';
  architectural_decisions: string = ''; // Current decision input
  savedDecisions: string[] = []; // List of saved decisions
  development_view_description: string = '';
  development_view_diagram: string = '';
  process_view_description: string = '';
  process_view_diagram: string = '';
  physical_view_description: string = '';
  physical_view_diagram: string = '';

  scenarioName: string = '';
  scenarioAttribute: string = '';
  scenarioEnvironment: string = '';
  scenarioStimulus: string = '';
  scenarioResponse: string = '';

  quality_criteria_name: string = '';
  quality_criteria_question: string = '';

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
  

  // Adds system purpose to the architecture context
addSystemPurpose() {
  const parsedContext = JSON.parse(this.architecture_context); // Parse the JSON string into an object

  if (this.systemPurpose.trim()) {
    parsedContext.architectureDescription['systemPurpose'] = this.systemPurpose.trim();
    this.systemPurpose = ''; // Clear the input field
    this.architecture_context = JSON.stringify(parsedContext); // Convert back to a string
    alert('System purpose added successfully!');
  } else {
    alert('Please enter a valid system purpose.');
  }
}

// Adds system constraint to the architecture context
addConstraint() {
  const parsedContext = JSON.parse(this.architecture_context); // Parse the JSON string into an object

  if (this.systemConstraint.trim()) {
    if (!parsedContext.architectureDescription['technicalConstraints']) {
      parsedContext.architectureDescription['technicalConstraints'] = [];
    }
    parsedContext.architectureDescription['technicalConstraints'].push(this.systemConstraint.trim());
    this.systemConstraint = ''; // Clear the input field
    this.architecture_context = JSON.stringify(parsedContext); // Convert back to a string
    alert('System constraint added successfully!');
  } else {
    alert('Please enter a valid system constraint.');
  }
}

// Adds system interaction to the architecture context
addInteraction() {
  const parsedContext = JSON.parse(this.architecture_context); // Parse the JSON string into an object

  if (this.systemInteraction.trim()) {
    if (!parsedContext.architectureDescription['systemInteractions']) {
      parsedContext.architectureDescription['systemInteractions'] = [];
    }
    parsedContext.architectureDescription['systemInteractions'].push(this.systemInteraction.trim());
    this.systemInteraction = ''; // Clear the input field
    this.architecture_context = JSON.stringify(parsedContext); // Convert back to a string
    alert('System interaction added successfully!');
  } else {
    alert('Please enter a valid system interaction.');
  }
}


  uploadInputs() {
    // Ensure all fields have values
    if (
      Object.keys(this.architecture_context).length === 0 ||
      !this.architecture_context?.trim() ||
      !this.architectural_approaches?.trim() ||
      !this.quality_criteria?.trim() ||
      !this.scenarios.trim()
    ) {
      alert('Please fill in all required fields.');
      return;
    }

    // Ensure all fields contain valid JSON
    let approachesJson, criteriaJson, scenariosJson, contextJson;
    try {
      approachesJson = JSON.parse(this.architectural_approaches);
      criteriaJson = JSON.parse(this.quality_criteria);
      scenariosJson = JSON.parse(this.scenarios);
      contextJson = JSON.parse(this.architecture_context);
    } catch (error) {
      alert('Please ensure all text fields contain valid JSON.');
      return;
    }

    // Prepare the JSON object to send to the backend
    const requestBody = {
      architecture_context: contextJson,
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
    this.architecture_context = '{ "architectureDescription": {}}'; // Initialize as an empty object
    this.architectural_approaches = '{"architecturalApproaches": []}';
    this.quality_criteria = '{ "quality_criteria" : [] }';
    this.scenarios = '{ "scenarios" : [] }';
    this.systemPurpose = '';
    this.systemConstraint = '';
    this.systemInteraction = '';

    this.approach_name = '';
    this.approach_description = '';
    this.architectural_decisions = ''; // Current decision input
    this.savedDecisions = []; // List of saved decisions
    this.development_view_description = '';
    this.development_view_diagram = '';
    this.process_view_description = '';
    this.process_view_diagram = '';
    this.physical_view_description = '';
    this.physical_view_diagram = '';

    this.scenarioName = '';
    this.scenarioAttribute = '';
    this.scenarioEnvironment = '';
    this.scenarioStimulus = '';
    this.scenarioResponse = '';
  
    this.quality_criteria_name = '';
    this.quality_criteria_question = '';

    this.inputsUploaded = false; // Flag to track if inputs have been uploaded
    this.loading = false; // New loading state

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

  addQualityAttributeCriterion() {
    if (!this.quality_criteria_name.trim() || !this.quality_criteria_question.trim()) {
      alert('Please fill out both fields before adding a criterion.');
      return;
    }
  
    // Parse the existing quality criteria or initialize it
    if (!this.quality_criteria.trim()) {
      this.quality_criteria = '{"quality_criteria": []}';
    }
  
    let criteriaJson;
    try {
      criteriaJson = JSON.parse(this.quality_criteria);
    } catch (error) {
      console.error('Error parsing quality criteria:', error);
      alert('Invalid quality criteria format. Resetting.');
      this.quality_criteria = '{"quality_criteria": []}';
      criteriaJson = { quality_criteria: [] };
    }
  
    // Create the new quality criterion
    const newCriterion = {
      name: this.quality_criteria_name.trim(),
      question: this.quality_criteria_question.trim()
    };
  
    // Add the new criterion to the array
    criteriaJson.quality_criteria.push(newCriterion);
  
    // Update the quality criteria field as a JSON string
    this.quality_criteria = JSON.stringify(criteriaJson, null, 2);
  
    // Clear the input fields
    this.quality_criteria_name = '';
    this.quality_criteria_question = '';
  
    alert('Quality attribute criterion added successfully!');
  }
  
  
  saveDecisions() {
    const decisionsArray = this.architectural_decisions
      .split('\n')
      .map((decision) => decision.trim())
      .filter((decision) => decision); // Remove empty lines

    this.savedDecisions = [...this.savedDecisions, ...decisionsArray];
    this.architectural_decisions = ''; // Clear the text area after saving
    alert('Decisions saved successfully!');
  }

  addArchitecturalApproach() {
    // Check if required text fields are filled
    if (
      !this.approach_name.trim() ||
      !this.approach_description.trim() ||
      !this.development_view_description.trim() ||
      !this.development_view_diagram.trim() ||
      !this.process_view_description.trim() ||
      !this.process_view_diagram.trim() ||
      !this.physical_view_description.trim() ||
      !this.physical_view_diagram.trim()
    ) {
      alert('Please fill out all text fields.');
      return;
    }
  
    // Check if the architectural decisions list is not empty
    if (this.savedDecisions.length === 0) {
      alert('The architectural decisions list cannot be empty.');
      return;
    }
  
    let approachesJson;
    try {
      approachesJson = JSON.parse(this.architectural_approaches);
    } catch (error) {
      console.error('Error parsing architectural approaches:', error);
      alert('Invalid architectural approaches format. Resetting.');
      this.architectural_approaches = '{"architecturalApproaches": []}';
      approachesJson = { architecturalApproaches: [] };
    }
  
    const newApproach = {
      approach: this.approach_name.trim(),
      description: this.approach_description.trim(),
      "architectural decisions": this.savedDecisions,
      "architectural views": [
        {
          view: "Development View",
          description: this.development_view_description.trim(),
          diagram: this.development_view_diagram.trim(),
        },
        {
          view: "Process View",
          description: this.process_view_description.trim(),
          diagram: this.process_view_diagram.trim(),
        },
        {
          view: "Physical View",
          description: this.physical_view_description.trim(),
          diagram: this.physical_view_diagram.trim(),
        },
      ],
    };
  
    approachesJson.architecturalApproaches.push(newApproach);
  
    this.architectural_approaches = JSON.stringify(approachesJson, null, 2);
  
    // Clear fields
    this.approach_name = '';
    this.approach_description = '';
    this.savedDecisions = []; // Clear saved decisions
    this.architectural_decisions = ''; // Clear the decision input field
    this.development_view_description = '';
    this.development_view_diagram = '';
    this.process_view_description = '';
    this.process_view_diagram = '';
    this.physical_view_description = '';
    this.physical_view_diagram = '';
  
    alert('Architectural approach added successfully!');
  }
  

  get formattedScenarios(): string {
    try {
      return JSON.stringify(JSON.parse(this.scenarios || '{ "scenarios" : [] }'), null, 2); // Beautify JSON
    } catch (error) {
      return 'Invalid JSON'; // Handle invalid JSON case
    }
  }  
  
  get formattedQualityCriteria(): string {
    try {
      return JSON.stringify(JSON.parse(this.quality_criteria || '{ "quality_criteria" : [] }'), null, 2); // Beautify JSON
    } catch (error) {
      return 'Invalid JSON'; // Handle invalid JSON case
    }
  }  

  get formattedApproaches(): string {
    try {
      return JSON.stringify(JSON.parse(this.architectural_approaches || '{ "architecturalApproaches" : []}'), null, 2); // Beautify JSON
    } catch (error) {
      return 'Invalid JSON'; // Handle invalid JSON case
    }
  }

  get formattedArchitectureContext(): string {
    try {
      return JSON.stringify(JSON.parse(this.architecture_context) || '{ "architectureDescription": {}}', null, 2); // Beautify JSON
    } catch (error) {
      return 'Invalid JSON'; // Handle invalid JSON case
    }
  }
}
