import { Question } from './question.model';

export interface Game {
  gameId: string;
  creator: string;
  currentQuestion: Question | null;
  askedQuestions: Question[];
  newQuestions: Question[];
}
