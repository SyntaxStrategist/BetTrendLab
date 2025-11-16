'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api, TodaysGamesResponse } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export default function RecommendationsPage() {
  const [games, setGames] = useState<TodaysGamesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getTodaysGames();
      setGames(data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to load today\'s games. Please check your backend connection.'
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Daily Recommendations</h1>
          <p className="text-muted-foreground text-lg">
            Today's games with predictions and analysis
          </p>
          {games && (
            <p className="text-sm text-muted-foreground mt-2">
              Date: {games.date} • {games.count} game{games.count !== 1 ? 's' : ''}
            </p>
          )}
        </div>
        <Button onClick={fetchGames} disabled={loading} variant="outline">
          {loading ? 'Loading...' : 'Refresh'}
        </Button>
      </div>

      {loading && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading today's games...</p>
        </div>
      )}

      {error && (
        <Card className="mb-6 border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <Button onClick={fetchGames} className="mt-4" variant="outline">
              Try Again
            </Button>
          </CardContent>
        </Card>
      )}

      {games && games.games.length === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>No Games Today</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              There are no games scheduled for today. Check back tomorrow!
            </p>
          </CardContent>
        </Card>
      )}

      {games && games.games.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2">
          {games.games.map((game, index) => {
            const favorite =
              game.homeWinProbability > game.awayWinProbability
                ? game.homeTeam
                : game.awayTeam;
            const favoriteProb = Math.max(
              game.homeWinProbability,
              game.awayWinProbability
            );

            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl">Game {index + 1}</CardTitle>
                    {game.gameTime && (
                      <Badge variant="outline">{game.gameTime}</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div className="text-center flex-1">
                      <p className="font-semibold text-lg">{game.homeTeam}</p>
                      <Badge variant="default" className="mt-2">Home</Badge>
                      <p className="text-sm text-muted-foreground mt-2">
                        {(game.homeWinProbability * 100).toFixed(1)}% win probability
                      </p>
                    </div>
                    <span className="mx-4 text-2xl font-bold">vs</span>
                    <div className="text-center flex-1">
                      <p className="font-semibold text-lg">{game.awayTeam}</p>
                      <Badge variant="outline" className="mt-2">Away</Badge>
                      <p className="text-sm text-muted-foreground mt-2">
                        {(game.awayWinProbability * 100).toFixed(1)}% win probability
                      </p>
                    </div>
                  </div>

                  <div className="p-4 rounded-lg bg-primary/10">
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground mb-1">Predicted Score</p>
                      <p className="text-2xl font-bold">{game.predictedScore}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Expected Total: {game.expectedTotal.toFixed(1)}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Favorite</span>
                      <Badge variant="default">{favorite}</Badge>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full"
                        style={{ width: `${favoriteProb * 100}%` }}
                      />
                    </div>
                    <p className="text-xs text-muted-foreground text-center">
                      {favorite} has a {(favoriteProb * 100).toFixed(1)}% chance to win
                    </p>
                  </div>

                  <div className="pt-4 border-t grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Home Win</p>
                      <p className="font-semibold">
                        {(game.homeWinProbability * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Away Win</p>
                      <p className="font-semibold">
                        {(game.awayWinProbability * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

