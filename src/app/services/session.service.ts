import { Injectable } from '@angular/core';

interface StoredSession {
  playerName: string;
  isCreator: boolean;
}

/**
 * Keeps track of "who am I in this game" in localStorage, keyed by gameId,
 * so a page refresh on /game/:gameId doesn't lose the player's name or
 * whether they are the creator (and therefore see the "New question" control).
 */
@Injectable({
  providedIn: 'root'
})
export class SessionService {
  private readonly keyPrefix = 'poser:session:';

  save(gameId: string, playerName: string, isCreator: boolean): void {
    const value: StoredSession = { playerName, isCreator };
    localStorage.setItem(this.keyPrefix + gameId, JSON.stringify(value));
  }

  load(gameId: string): StoredSession | null {
    const raw = localStorage.getItem(this.keyPrefix + gameId);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as StoredSession;
    } catch {
      return null;
    }
  }

  clear(gameId: string): void {
    localStorage.removeItem(this.keyPrefix + gameId);
  }
}
