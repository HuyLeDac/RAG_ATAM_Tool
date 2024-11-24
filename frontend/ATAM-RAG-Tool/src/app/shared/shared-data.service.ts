import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedDataService {
  private resultsSource = new BehaviorSubject<any>(null); // Holds the results data
  currentResults = this.resultsSource.asObservable(); // Observable for components to subscribe to

  constructor() {}

  updateResults(results: any) {
    this.resultsSource.next(results); // Update the results data
  }
}
