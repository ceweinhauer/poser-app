import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { DataService } from '../../services/data.service';
import { SessionService } from '../../services/session.service';

type Mode = 'create' | 'join';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {
  mode: Mode = 'create';
  playerName = '';
  gameCode = '';
  isSubmitting = false;
  errorMessage = '';

  constructor(
    private dataService: DataService,
    private sessionService: SessionService,
    private router: Router
  ) {}

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
      this.dataService.createGame(name).subscribe({
        next: ({ gameId }) => {
          this.sessionService.save(gameId, name, true);
          this.router.navigate(['/game', gameId]);
        },
        error: () => {
          this.isSubmitting = false;
          this.errorMessage = 'Could not start a game right now. Try again.';
        }
      });
    } else {
      const code = this.gameCode.trim().toUpperCase();
      this.dataService.joinGame(code, name).subscribe({
        next: () => {
          this.sessionService.save(code, name, false);
          this.router.navigate(['/game', code]);
        },
        error: () => {
          this.isSubmitting = false;
          this.errorMessage = "That code didn't match a game. Double check it and try again.";
        }
      });
    }
  }
}
