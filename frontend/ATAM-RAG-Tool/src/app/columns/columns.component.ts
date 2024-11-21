import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http'; 
import { FormsModule } from '@angular/forms'; 

@Component({
  selector: 'app-columns',
  standalone: true,
  imports: [HttpClientModule, FormsModule],
  templateUrl: './columns.component.html',
  styleUrls: ['./columns.component.scss']
})

export class ColumnsComponent implements OnInit {
  architectureContext: any;
  architecturalApproaches: any;
  qualityAttributeCriteria: any;
  scenarios: any;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // ... your initialization logic here
  };

  checkAndstartAnalysisProcess() {
    // Ensure all fields have values
    if (
      !this.architectureContext?.trim() ||
      !this.architecturalApproaches?.trim() ||
      !this.qualityAttributeCriteria?.trim() ||
      !this.scenarios?.trim()
    ) {
      alert('Please fill in all text fields.');
      return;
    }
  
    // Ensure all fields contain valid JSON
    let contextJson, approachesJson, criteriaJson, scenariosJson;
    try {
      contextJson = JSON.parse(this.architectureContext);
      approachesJson = JSON.parse(this.architecturalApproaches);
      criteriaJson = JSON.parse(this.qualityAttributeCriteria);
      scenariosJson = JSON.parse(this.scenarios);
    } catch (error) {
      alert('Please ensure all text fields contain valid JSON.');
      return;
    }
  
    // Prepare the JSON object to send to the backend
    const requestBody = {
      architectureContext: contextJson,
      architecturalApproaches: approachesJson,
      qualityAttributeCriteria: criteriaJson,
      scenarios: scenariosJson
    };
  
    // Send the JSON object to the backend using POST
    this.http.post('http://127.0.0.1:5000/start-analysis', requestBody)
      .subscribe(
        response => {
          console.log('Analysis started successfully:', response);
          alert('Analysis process started successfully!');
        },
        error => {
          console.error('Error during HTTP request:', error);
          alert('An error occurred while starting the analysis process.');
        }
      );
  }
  
  
}