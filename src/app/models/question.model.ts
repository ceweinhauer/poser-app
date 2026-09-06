import { Answer } from './answer.model';

export interface Question {
  questionText: string;
  questionAsker: string;
  upvotes: number;
  downvotes: number;
  answers: Answer[];
}
