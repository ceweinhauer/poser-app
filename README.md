# Poser

A small party game: someone creates a game, everyone else joins with a code,
and players submit questions anonymously ("who would...", "what's your...").
The creator reveals questions one at a time and the group guesses who wrote it.

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
interface Question {
  questionText: string;
  questionAsker: string;
}

interface Game {
  gameId: string;
  creator: string;
  currentQuestion: Question | null;
  askedQuestions: Question[];
  newQuestions: Question[];
}
```

## Backend contract expected by `DataService`

| Method | Endpoint                          | Body                                      | Returns          |
|--------|------------------------------------|----------------------------------------  |-------------------|
| POST   | `/games`                           | `{ creatorName }`                        | `{ gameId }`      |
| GET    | `/games/:gameId`                   | —                                        | `Game`            |
| POST   | `/games/join`                      | `{ name, gameId }`                       | `Game`            |
| POST   | `/games/add_question`              | `{ questionAsker, questionText, gameId }`| `Game`            |
| POST   | `/games/next`                      | `{gameId}`                               | `Game`            |

Notes for the backend implementation:
- `createGame` should generate a short, easy-to-type `gameId` (e.g. 4-6
  uppercase alphanumeric characters) and store a new game document with the
  given `creator`, empty `askedQuestions`/`newQuestions`, and a `null`
  `currentQuestion`.
- `submitQuestion` appends `{ questionText, questionAsker }` to that game's
  `newQuestions` array and returns the updated game.
- `nextQuestion` should push the current `currentQuestion` onto
  `askedQuestions` (if one exists), pick a random entry out of
  `newQuestions`, remove it from that list, and set it as the new
  `currentQuestion`.
- `join` just needs to confirm the `gameId` exists (404 if not) — the
  frontend uses this to validate a code before entering the game screen.

The frontend polls `GET /games/:gameId` every 4 seconds while on the game
screen so all players stay roughly in sync without needing websockets.

## How the frontend decides who is "the creator"

There's no auth — whoever's browser called `createGame` is remembered
locally (`localStorage`, keyed by `gameId`) as the creator for that game, and
only they see the "New question" control. Anyone with the code can join and
submit questions.

## Mobile & desktop

There's no device-sniffing — the layout is fluid (single centered column,
`clamp()`-based type scale, `rem`/`%`-based spacing, minimum 44px tap
targets) so it reads well from a small phone up through a desktop browser
without separate mobile/desktop code paths.
