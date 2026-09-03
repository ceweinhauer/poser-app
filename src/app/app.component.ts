import { Component } from '@angular/core';
import { Router, NavigationStart, NavigationEnd, NavigationCancel, NavigationError } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
  constructor(private router: Router) {
    // Temporary diagnostic logging - remove once navigation issue is resolved.
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationStart) {
        console.warn('[Router] NavigationStart ->', event.url);
      } else if (event instanceof NavigationEnd) {
        console.warn('[Router] NavigationEnd ->', event.urlAfterRedirects);
      } else if (event instanceof NavigationCancel) {
        console.warn('[Router] NavigationCancel ->', event.url, '| reason:', event.reason);
      } else if (event instanceof NavigationError) {
        console.warn('[Router] NavigationError ->', event.url, '| error:', event.error);
      }
    });
  }
}