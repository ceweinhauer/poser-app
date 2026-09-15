# Dish

A small party game: someone creates a game, everyone else joins with a code,
and players submit questions anonymously ("who would...", "what's your...").
The creator reveals questions one at a time, everyone guesses who wrote it,
and votes the question up or down.

This repo is the Angular 16 frontend only. It expects a backend (Python +
MongoDB, per your setup) that implements the REST contract below.

## Running locally

```bash
npm install
npm start
```

The app runs at `http://localhost:4200`. It talks to the API URL configured
in `src/environments/environment.ts` (defaults to `http://localhost:5000/api`
for local dev, `/api` in production — update these to match your backend).

## Data model

```ts
interface Answer {
  answerText: string;
  answerName: string;
  upvotes: number;
  downvotes: number;
}

interface Question {
  questionText: string;
  questionAsker: string;
  upvotes: number;
  downvotes: number;
  answers: Answer[];
}

interface Game {
  gameId: string;
  creator: string;
  players: string[];
  currentQuestion: Question | null;
  askedQuestions: Question[];
  newQuestions: Question[];
}
```

## Backend contract expected by `DataService`

| Method | Endpoint                          | Body                                  | Returns          |
|--------|------------------------------------|----------------------------------------|-------------------|
| POST   | `/games`                           | `{ creatorName }`                      | `{ gameId }`      |
| GET    | `/games/:gameId`                   | —                                       | `Game`            |
| POST   | `/games/:gameId/join`              | `{ name }`                             | `Game`            |
| POST   | `/games/:gameId/questions`         | `{ questionAsker, questionText }`      | `Game`            |
| POST   | `/games/:gameId/next`              | —                                       | `Game`            |
| POST   | `/games/:gameId/vote`              | `{ direction: 'up' \| 'down' }`        | `Game`            |
| POST   | `/games/:gameId/answers`           | `{ answerName, answerText }`           | `Game`            |
| POST   | `/games/:gameId/answers/vote`      | `{ answerName, answerText, direction: 'up' \| 'down' }` | `Game` |

Notes for the backend implementation:
- `createGame` should generate a short, easy-to-type `gameId` (e.g. 4-6
  uppercase alphanumeric characters) and store a new game document with the
  given `creator`, that creator already present in `players`, empty
  `askedQuestions`/`newQuestions`, and a `null` `currentQuestion`.
- `join` should confirm the `gameId` exists (404 if not), and append `name`
  to that game's `players` list if it isn't already present.
- `submitQuestion` appends `{ questionText, questionAsker, upvotes: 0,
  downvotes: 0, answers: [] }` to that game's `newQuestions` array and
  returns the updated game.
- `nextQuestion` should push the current `currentQuestion` onto
  `askedQuestions` (if one exists), pick a random entry out of
  `newQuestions`, remove it from that list, and set it as the new
  `currentQuestion`.
- `vote` should increment `upvotes` or `downvotes` on whichever question is
  currently `currentQuestion` and return the updated game. (No dedupe/one
  vote per player logic is enforced here — add that server-side if you want
  it.)
- `answers` (submit) should append `{ answerText, answerName, upvotes: 0,
  downvotes: 0 }` to the current question's `answers` array and return the
  updated game. Any player, including whoever asked the question, can
  submit one.
- `answers/vote` should find the matching answer on the current question by
  `answerName` + `answerText` and increment its `upvotes` or `downvotes`.

The frontend polls `GET /games/:gameId` every 4 seconds while on the game
screen so all players stay roughly in sync without needing websockets.

## How the frontend decides who is "the creator"

There's no auth — whoever's browser called `createGame` is remembered
locally (`localStorage`, keyed by `gameId`) as the creator for that game, and
only they see the "New question" control. Anyone with the code can join,
submit questions, guess, and vote.

## Guessing & scoring

The current question's `questionAsker` is present in the data the whole
time, but the UI deliberately never renders it while the question is
`currentQuestion` — the template only shows it once a question has moved
into `askedQuestions`.

While a question is live, each player (other than whoever asked it) picks a
name from a dropdown of `players` and locks it in — the "Correct! / Not
quite." banner that appears once the creator advances to the next question
is purely a personal reveal (it compares the locked guess to that outgoing
question's `questionAsker`) and does not compute score itself.

Scoring is backend-authoritative: `Game.scores` (`{ name, score }[]`) and
`Game.guesses` (`{ guesserName, guessedName }[]`) live on the `Game` model,
and `nextQuestion` is expected to tally scores there. The **Leaderboard**
button next to the game code opens a ranked view of `game.scores`, highest
first.

One piece is still open: `GameComponent.lockInGuess()` only sets local UI
state right now — it has a `TODO` where a `DataService.addGuess(gameId,
guesserName, guessedName)` call should go once that method exists, so a
locked-in guess actually reaches the backend's `guesses` list to be scored.

## Leaderboard

`src/app/models/score.model.ts` and `src/app/models/guess.model.ts` mirror
the `Score`/`Guess` shapes added to `Game`. The `Guess` field names
(`guesserName`, `guessedName`) are an assumption based on "add_guess takes
the user's name and the name of the person they're guessing" — rename them
in `guess.model.ts` (and wherever `addGuess` ends up being called) if your
backend uses different keys; nothing else depends on their exact names.

## Taglines

The rotating subtitle under the logo on the home page lives in
`HomeComponent.taglines` (`src/app/pages/home/home.component.ts`) as a plain
string array — add, remove, or edit entries there. One is picked at random
each time the page loads.

## Logo

`src/assets/logo.png` is a placeholder monogram — swap in your real logo at
that path (or update the `src` in `home.component.html` and
`game.component.html`) whenever it's ready.

## Mobile & desktop

There's no device-sniffing — the layout is fluid (single centered column,
`clamp()`-based type scale, `rem`/`%`-based spacing, minimum 44px tap
targets) so it reads well from a small phone up through a desktop browser
without separate mobile/desktop code paths.
