'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api, TeamsResponse } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function Home() {
  const [teams, setTeams] = useState<TeamsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await api.getTeams();
        setTeams(data);
      } catch (err) {
        setError('Failed to load data. Please check your backend connection.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const topTeams = teams?.teams
    .sort((a, b) => b.eloRating - a.eloRating)
    .slice(0, 5) || [];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">BetTrendLab</h1>
        <p className="text-muted-foreground text-lg">
          Advanced NBA betting analytics powered by ELO ratings and Poisson models
        </p>
      </div>

      {loading && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      )}

      {error && (
        <Card className="mb-6 border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Make sure your backend is running and NEXT_PUBLIC_API_URL is set correctly.
            </p>
          </CardContent>
        </Card>
      )}

      {teams && (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
            <Card>
              <CardHeader>
                <CardTitle>Total Teams</CardTitle>
                <CardDescription>Teams in our database</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{teams.count}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Rated Team</CardTitle>
                <CardDescription>Highest ELO rating</CardDescription>
              </CardHeader>
              <CardContent>
                {topTeams.length > 0 && (
                  <>
                    <div className="text-xl font-semibold mb-1">
                      {topTeams[0].team}
                    </div>
                    <Badge variant="default">
                      {topTeams[0].eloRating.toFixed(1)} ELO
                    </Badge>
                  </>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Average ELO</CardTitle>
                <CardDescription>Mean rating across all teams</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {teams.teams.length > 0
                    ? (
                        teams.teams.reduce((sum, t) => sum + t.eloRating, 0) /
                        teams.teams.length
                      ).toFixed(1)
                    : '0'}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Top 5 Teams by ELO Rating</CardTitle>
              <CardDescription>Current highest rated teams</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {topTeams.map((team, index) => (
                  <div
                    key={team.team}
                    className="flex items-center justify-between p-3 rounded-lg border"
                  >
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="w-8 text-center">
                        {index + 1}
                      </Badge>
                      <span className="font-medium">{team.team}</span>
                    </div>
                    <Badge>{team.eloRating.toFixed(1)}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader>
                <CardTitle>Rankings</CardTitle>
                <CardDescription>View all team rankings</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/rankings">
                  <Button className="w-full">View Rankings</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Predictions</CardTitle>
                <CardDescription>Predict game outcomes</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/prediction">
                  <Button className="w-full">Make Prediction</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Value Bets</CardTitle>
                <CardDescription>Find value betting opportunities</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/value-bet">
                  <Button className="w-full">Analyze Bets</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Daily Picks</CardTitle>
                <CardDescription>Today's recommendations</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/recommendations">
                  <Button className="w-full">View Picks</Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
