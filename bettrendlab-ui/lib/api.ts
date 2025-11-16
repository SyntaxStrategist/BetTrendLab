import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface TeamRating {
  team: string;
  eloRating: number;
}

export interface TeamsResponse {
  teams: TeamRating[];
  count: number;
}

export interface RankingItem {
  rank: number;
  team: string;
  eloRating: number;
}

export interface RankingsResponse {
  rankings: RankingItem[];
  updatedAt?: string;
}

export interface PredictionResponse {
  homeTeam: string;
  awayTeam: string;
  predictedScore: string;
  homeExpectedScore: number;
  awayExpectedScore: number;
  homeWinProbability: number;
  awayWinProbability: number;
  eloPrediction: {
    homeWinProbability: number;
    awayWinProbability: number;
  };
  poissonPrediction: {
    homeWinProbability: number;
    awayWinProbability: number;
  };
  expectedTotal: number;
}

export interface ValueBetAnalysis {
  team: string;
  betType: string;
  modelProbability: number;
  impliedProbability: number;
  odds: number;
  expectedValue: number;
  edge: number;
  isValueBet: boolean;
}

export interface ValueBetsResponse {
  homeTeam: string;
  awayTeam: string;
  homeAnalysis: ValueBetAnalysis;
  awayAnalysis: ValueBetAnalysis;
  expectedScore: string;
}

export interface GamePrediction {
  homeTeam: string;
  awayTeam: string;
  gameTime?: string;
  homeWinProbability: number;
  awayWinProbability: number;
  predictedScore: string;
  expectedTotal: number;
}

export interface TodaysGamesResponse {
  date: string;
  games: GamePrediction[];
  count: number;
}

export interface UpdateResponse {
  status: string;
  message: string;
  games_processed?: number;
  teams_updated?: number;
}

// API functions
export const api = {
  // Get all teams
  getTeams: async (): Promise<TeamsResponse> => {
    const response = await apiClient.get<TeamsResponse>('/teams');
    return response.data;
  },

  // Get rankings
  getRankings: async (): Promise<RankingsResponse> => {
    const response = await apiClient.get<RankingsResponse>('/rankings');
    return response.data;
  },

  // Get prediction
  getPrediction: async (
    team1: string,
    team2: string,
    homeTeam?: string
  ): Promise<PredictionResponse> => {
    const params = new URLSearchParams({
      team1,
      team2,
    });
    if (homeTeam) {
      params.append('home_team', homeTeam);
    }
    const response = await apiClient.get<PredictionResponse>(
      `/predict?${params.toString()}`
    );
    return response.data;
  },

  // Analyze value bets
  getValueBets: async (
    team1: string,
    team2: string,
    odds1: number,
    odds2: number,
    homeTeam?: string
  ): Promise<ValueBetsResponse> => {
    const params = new URLSearchParams({
      team1,
      team2,
      odds1: odds1.toString(),
      odds2: odds2.toString(),
    });
    if (homeTeam) {
      params.append('home_team', homeTeam);
    }
    const response = await apiClient.get<ValueBetsResponse>(
      `/value-bet?${params.toString()}`
    );
    return response.data;
  },

  // Get today's games
  getTodaysGames: async (): Promise<TodaysGamesResponse> => {
    const response = await apiClient.get<TodaysGamesResponse>('/games/today');
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Force update stats and ELO ratings
  updateData: async (): Promise<UpdateResponse> => {
    const response = await apiClient.post<UpdateResponse>('/api/v1/update');
    return response.data;
  },
};

