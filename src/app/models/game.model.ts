import { Guess } from './guess.model';
import { Question } from './question.model';
import { Score } from './score.model';

export interface Game {
  gameId: string;
  creator: string;
  currentQuestion: Question | null;
  askedQuestions: Question[];
  newQuestions: Question[];
  players: string[];
  scores: Score[];
  guesses: Guess[];
}
