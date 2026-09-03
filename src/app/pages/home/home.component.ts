import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs/operators';
import { DataService } from '../../services/data.service';
import { SessionService } from '../../services/session.service';

type Mode = 'create' | 'join';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  /**
   * Taglines shown under the logo on the home page. One is picked at
   * random each time the page loads. Add/edit/remove freely.
   */
  taglines: string[] = [
    'Guess who said it.',
    'Everyone has an opinion. Find the source.',
    'Anonymous questions. Not-so-anonymous answers.',
    'Who\'s the poser this round?'
  ];
  tagline = this.pickTagline();

  mode: Mode = 'create';
  playerName = '';
  gameCode = '';
  isSubmitting = false;
  errorMessage = '';

  constructor(
    private dataService: DataService,
    private sessionService: SessionService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // A share link looks like https://your-app/?code=ABCD - land straight
    // on the join tab with the code already filled in.
    const sharedCode = this.route.snapshot.queryParamMap.get('code');
    if (sharedCode) {
      this.mode = 'join';
      this.gameCode = sharedCode.toUpperCase();
    }
  }

  private pickTagline(): string {
    if (!this.taglines.length) {
      return '';
    }
    const index = Math.floor(Math.random() * this.taglines.length);
    return this.taglines[index];
  }

  setMode(mode: Mode): void {
    this.mode = mode;
    this.errorMessage = '';
  }

  get canContinue(): boolean {
    if (!this.playerName.trim()) {
      return false;
    }
    if (this.mode === 'join' && !this.gameCode.trim()) {
      return false;
    }
    return true;
  }

  continue(): void {
    if (!this.canContinue || this.isSubmitting) {
      return;
    }
    const name = this.playerName.trim();
    this.isSubmitting = true;
    this.errorMessage = '';

    if (this.mode === 'create') {
      this.dataService.createGame(name)
        .pipe(finalize(() => (this.isSubmitting = false)))
        .subscribe({
          next: ({ gameId }) => {
            this.sessionService.save(gameId, name, true);
            this.router.navigate(['/game', gameId]);
          },
          error: () => {
            this.errorMessage = 'Could not start a game right now. Try again.';
          }
        });
    } else {
      const code = this.gameCode.trim().toUpperCase();
      this.dataService.joinGame(code, name)
        .pipe(finalize(() => (this.isSubmitting = false)))
        .subscribe({
          next: () => {
            this.sessionService.save(code, name, false);
            this.router.navigate(['/game', code]);
          },
          error: () => {
            this.errorMessage = "That code didn't match a game. Double check it and try again.";
          }
        });
    }
  }
}
