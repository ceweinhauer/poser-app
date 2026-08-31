import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription, interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';
import { DataService } from '../../services/data.service';
import { SessionService } from '../../services/session.service';
import { Game } from '../../models/game.model';

const POLL_INTERVAL_MS = 4000;

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.scss']
})
export class GameComponent implements OnInit, OnDestroy {
  gameId = '';
  playerName = '';
  isCreator = false;

  game: Game | null = null;
  loadError = '';

  newQuestionText = '';
  isSubmittingQuestion = false;
  isAdvancing = false;
  submitConfirmation = '';

  private pollSub?: Subscription;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dataService: DataService,
    private sessionService: SessionService
  ) {}

  ngOnInit(): void {
    const gameId = this.route.snapshot.paramMap.get('gameId');
    if (!gameId) {
      this.router.navigate(['/']);
      return;
    }
    this.gameId = gameId;

    const session = this.sessionService.load(gameId);
    if (!session) {
      // No local record of joining/creating this game (e.g. link opened fresh).
      this.router.navigate(['/']);
      return;
    }
    this.playerName = session.playerName;
    this.isCreator = session.isCreator;

    this.pollSub = interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.dataService.getGame(this.gameId))
      )
      .subscribe({
        next: (game) => {
          this.game = game;
          this.loadError = '';
        },
        error: () => {
          this.loadError = "Couldn't reach the game. Retrying...";
        }
      });
  }

  ngOnDestroy(): void {
    this.pollSub?.unsubscribe();
  }

  get hasAvailableQuestions(): boolean {
    return !!this.game && this.game.newQuestions.length > 0;
  }

  submitQuestion(): void {
    const text = this.newQuestionText.trim();
    if (!text || this.isSubmittingQuestion) {
      return;
    }
    this.isSubmittingQuestion = true;
    this.submitConfirmation = '';

    this.dataService.submitQuestion(this.gameId, this.playerName, text).subscribe({
      next: (game) => {
        this.game = game;
        this.newQuestionText = '';
        this.isSubmittingQuestion = false;
        this.submitConfirmation = 'Question added to the pile.';
      },
      error: () => {
        this.isSubmittingQuestion = false;
        this.submitConfirmation = "Couldn't submit that question. Try again.";
      }
    });
  }

  advanceQuestion(): void {
    if (this.isAdvancing) {
      return;
    }
    this.isAdvancing = true;
    this.dataService.nextQuestion(this.gameId).subscribe({
      next: (game) => {
        this.game = game;
        this.isAdvancing = false;
      },
      error: () => {
        this.isAdvancing = false;
      }
    });
  }

  copyCode(): void {
    if (!navigator.clipboard) {
      return;
    }
    navigator.clipboard.writeText(this.gameId).catch(() => undefined);
  }
}
