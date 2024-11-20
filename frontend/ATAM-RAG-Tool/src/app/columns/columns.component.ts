import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http'; 

@Component({
  selector: 'app-columns',
  standalone: true,
  imports: [HttpClientModule],
  templateUrl: './columns.component.html',
  styleUrls: ['./columns.component.scss']
})

export class ColumnsComponent implements OnInit {

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // ... your initialization logic here
  }

  startAnalysisProcess() {
    this.http.get('http://127.0.0.1:5000/get-results')
      .subscribe(response => {
        console.log(response);
        // Handle the response data here
      });
  }
}