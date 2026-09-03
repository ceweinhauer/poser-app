import { Injectable } from '@angular/core';

interface StoredSession {
  playerName: string;
  isCreator: boolean;
  score: number;
}

/**
 * Keeps track of "who am I in this game" in localStorage, keyed by gameId,
 * so a page refresh on /game/:gameId doesn't lose the player's name,
 * whether they are the creator, or their running guess score.
 */
@Injectable({
  providedIn: 'root'
})
export class SessionService {
  private readonly keyPrefix = 'dish:session:';

  save(gameId: string, playerName: string, isCreator: boolean, score = 0): void {
    const value: StoredSession = { playerName, isCreator, score };
    localStorage.setItem(this.keyPrefix + gameId, JSON.stringify(value));
  }

  saveScore(gameId: string, score: number): void {
    const existing = this.load(gameId);
    if (!existing) {
      return;
    }
    this.save(gameId, existing.playerName, existing.isCreator, score);
  }

  load(gameId: string): StoredSession | null {
    const raw = localStorage.getItem(this.keyPrefix + gameId);
    if (!raw) {
      return null;
    }
    try {
      const parsed = JSON.parse(raw) as Partial<StoredSession>;
      return {
        playerName: parsed.playerName ?? '',
        isCreator: !!parsed.isCreator,
        score: parsed.score ?? 0
      };
    } catch {
      return null;
    }
  }

  clear(gameId: string): void {
    localStorage.removeItem(this.keyPrefix + gameId);
  }
}