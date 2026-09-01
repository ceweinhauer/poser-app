import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Game } from '../models/game.model';


@Injectable({
  providedIn: 'root'
})
export class DataService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Creates a new game for the given creator name.
   * Returns the newly created gameId.
   */
  createGame(creatorName: string): Observable<{ gameId: string }> {
    return this.http.post<{ gameId: string }>(`${this.baseUrl}/games`, { creatorName });
  }

  /**
   * Submits a new question for a given game. The backend appends it to
   * that game's newQuestions list.
   */
  submitQuestion(gameId: string, questionAsker: string, questionText: string): Observable<Game> {
    return this.http.post<Game>(`${this.baseUrl}/games/questions`, {
      questionAsker,
      questionText,
      gameId
    });
  }

  /**
   * Moves the current question into askedQuestions and randomly promotes
   * a question from newQuestions to be the new currentQuestion.
   */
  nextQuestion(gameId: string): Observable<Game> {
    return this.http.post<Game>(`${this.baseUrl}/games/next`, {
      gameId
    });
  }

  /**
   * Validates a game code exists and registers the joining player.
   */
  joinGame(gameId: string, name: string): Observable<Game> {
    return this.http.post<Game>(`${this.baseUrl}/games/join`, { name, gameId });
  }

  /**
   * Fetches the current state of a game. Used on load and while polling
   * for updates from other players.
   */
  getGame(gameId: string): Observable<Game> {
    return this.http.get<Game>(`${this.baseUrl}/games/${gameId}`);
  }
}
