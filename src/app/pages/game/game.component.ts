import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription, interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';
import { DataService } from '../../services/data.service';
import { SessionService } from '../../services/session.service';
import { Game } from '../../models/game.model';
import { Question } from '../../models/question.model';

const POLL_INTERVAL_MS = 4000;

interface RevealResult {
  correct: boolean;
  guessedAsker: string;
  actualAsker: string;
  questionText: string;
}

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.scss']
})
export class GameComponent implements OnInit, OnDestroy {
  gameId = '';
  playerName = '';
  isCreator = false;
  score = 0;

  game: Game | null = null;
  loadError = '';

  newQuestionText = '';
  isSubmittingQuestion = false;
  isAdvancing = false;
  submitConfirmation = '';

  isVoting = false;
  hasVotedOnCurrentQuestion = false;

  shareStatus = '';

  // --- Guessing state (who asked the current question) ---
  myGuess = '';
  guessLocked = false;
  lastResult: RevealResult | null = null;

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
    this.score = session.score;

    this.pollSub = interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.dataService.getGame(this.gameId))
      )
      .subscribe({
        next: (game) => this.applyGameUpdate(game),
        error: () => {
          this.loadError = "Couldn't reach the game. Retrying...";
        }
      });
  }

  ngOnDestroy(): void {
    this.pollSub?.unsubscribe();
  }

  /**
   * Applies a freshly-fetched game state. If the current question changed
   * since the last update and the player had locked in a guess, this is
   * where the guess gets scored against the question that just rolled off
   * into askedQuestions.
   */
  private applyGameUpdate(game: Game): void {
    const previousQuestion = this.game?.currentQuestion ?? null;
    const nextQuestionText = game.currentQuestion?.questionText ?? null;
    const questionChanged = !!previousQuestion && previousQuestion.questionText !== nextQuestionText;

    if (questionChanged && this.guessLocked && this.myGuess) {
      const actualAsker = previousQuestion!.questionAsker;
      this.lastResult = {
        correct: this.myGuess === actualAsker,
        guessedAsker: this.myGuess,
        actualAsker,
        questionText: previousQuestion!.questionText
      };
      if (this.lastResult.correct) {
        this.score += 1;
        this.sessionService.saveScore(this.gameId, this.score);
      }
    }

    if (questionChanged) {
      this.myGuess = '';
      this.guessLocked = false;
      this.hasVotedOnCurrentQuestion = false;
    }

    this.game = game;
    this.loadError = '';
  }

  /** Players available to guess from - everyone except the current viewer. */
  get guessableUsers(): string[] {
    if (!this.game) {
      return [];
    }
    return this.game.players.filter((p) => p !== this.playerName);
  }

  /** True when the logged-in player is the one who asked the current question. */
  get isOwnQuestion(): boolean {
    return !!this.game?.currentQuestion && this.game.currentQuestion.questionAsker === this.playerName;
  }

  get hasAvailableQuestions(): boolean {
    return !!this.game && this.game.newQuestions.length > 0;
  }

  lockInGuess(): void {
    if (!this.myGuess || this.guessLocked) {
      return;
    }
    this.guessLocked = true;
  }

  changeGuess(): void {
    this.guessLocked = false;
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
        this.applyGameUpdate(game);
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
        this.applyGameUpdate(game);
        this.isAdvancing = false;
      },
      error: () => {
        this.isAdvancing = false;
      }
    });
  }

  vote(direction: 'up' | 'down'): void {
    if (this.isVoting || this.hasVotedOnCurrentQuestion || !this.game?.currentQuestion) {
      return;
    }
    this.isVoting = true;
    this.hasVotedOnCurrentQuestion = true;
    this.dataService.voteQuestion(this.gameId, direction).subscribe({
      next: (game) => {
        this.applyGameUpdate(game);
        this.isVoting = false;
      },
      error: () => {
        this.isVoting = false;
        this.hasVotedOnCurrentQuestion = false;
      }
    });
  }

  trackByQuestionText(_index: number, question: Question): string {
    return question.questionText;
  }

  copyCode(): void {
    if (!navigator.clipboard) {
      return;
    }
    navigator.clipboard.writeText(this.gameId).catch(() => undefined);
  }

  /**
   * Opens the native share sheet on phones (Messages, WhatsApp, etc.) with
   * an invite message and a link that pre-fills the game code on the join
   * screen. Falls back to copying the message to the clipboard on browsers
   * without the Web Share API (most desktops).
   */
  async shareGame(): Promise<void> {
    const shareUrl = `${window.location.origin}/?code=${this.gameId}`;
    const shareText = `Join my game of Dish! Code: ${this.gameId}`;

    if (navigator.share) {
      try {
        await navigator.share({ title: 'Dish', text: shareText, url: shareUrl });
      } catch {
        // User backed out of the share sheet - nothing to do.
      }
      return;
    }

    const fallbackMessage = `${shareText} ${shareUrl}`;
    if (navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(fallbackMessage);
        this.shareStatus = 'Invite copied to clipboard.';
      } catch {
        this.shareStatus = 'Could not copy the invite.';
      }
    } else {
      this.shareStatus = fallbackMessage;
    }
    setTimeout(() => (this.shareStatus = ''), 4000);
  }
}
