# BetTrendLab UI

A modern Next.js 15 frontend for BetTrendLab - NBA betting analytics platform.

## Features

- **Home Page**: Overview dashboard with team statistics and quick navigation
- **Rankings Page**: Complete ELO ratings table for all NBA teams
- **Prediction Page**: Game outcome predictions using ELO and Poisson models
- **Value Bet Page**: Analyze betting odds to find value opportunities
- **Daily Recommendations**: Today's games with automated predictions

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- TailwindCSS
- shadcn/ui components
- Axios for API communication

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file in the root directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Railway deployment, update with your backend URL:
```env
NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment to Vercel

1. Push your code to GitHub
2. Import your repository in Vercel
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Railway backend URL
4. Deploy!

The project is configured for Vercel deployment with `vercel.json`.

## Project Structure

```
bettrendlab-ui/
├── app/
│   ├── page.tsx              # Home page
│   ├── rankings/
│   │   └── page.tsx          # Rankings page
│   ├── prediction/
│   │   └── page.tsx          # Prediction page
│   ├── value-bet/
│   │   └── page.tsx          # Value bet analyzer
│   ├── recommendations/
│   │   └── page.tsx          # Daily recommendations
│   ├── layout.tsx            # Root layout with navigation
│   └── globals.css           # Global styles
├── components/
│   ├── navigation.tsx        # Navigation component
│   └── ui/                   # shadcn/ui components
├── lib/
│   ├── api.ts                # API client with Axios
│   └── utils.ts              # Utility functions
└── vercel.json               # Vercel configuration
```

## API Integration

The frontend connects to the BetTrendLab backend API. Make sure your backend is running and accessible at the URL specified in `NEXT_PUBLIC_API_URL`.

### API Endpoints Used

- `GET /teams` - Get all teams with ELO ratings
- `GET /rankings` - Get full rankings table
- `GET /predict` - Get game prediction
- `GET /value-bet` - Analyze value bets
- `GET /games/today` - Get today's games with predictions

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
