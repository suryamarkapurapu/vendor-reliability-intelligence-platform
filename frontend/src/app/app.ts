import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { inject as injectAnalytics } from '@vercel/analytics';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  title = 'Vendor Reliability Platform';

  constructor() {
    // Initialize Vercel Analytics with SSR safety check
    if (typeof window !== 'undefined') {
      injectAnalytics();
    }
  }
}
