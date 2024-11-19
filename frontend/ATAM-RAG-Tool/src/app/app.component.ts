import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { ColumnsComponent } from './columns/columns.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, ColumnsComponent], // Correct imports
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'] // Corrected to styleUrls (plural)
})
export class AppComponent {
  title = 'ATAM-RAG-Tool';
}
