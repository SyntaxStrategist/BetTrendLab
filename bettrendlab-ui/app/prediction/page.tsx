'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api, PredictionResponse, TeamRating } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

export default function PredictionPage() {
  const [teams, setTeams] = useState<TeamRating[]>([]);
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [homeTeam, setHomeTeam] = useState('');
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const data = await api.getTeams();
        setTeams(data.teams);
      } catch (err) {
        console.error('Failed to load teams:', err);
      }
    };

    fetchTeams();
  }, []);

  const handlePredict = async () => {
    if (!team1 || !team2) {
      setError('Please select both teams');
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await api.getPrediction(
        team1,
        team2,
        homeTeam || undefined
      );
      setPrediction(result);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to get prediction. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Game Prediction</h1>
        <p className="text-muted-foreground text-lg">
          Predict game outcomes using ELO ratings and Poisson models
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Select Teams</CardTitle>
            <CardDescription>Choose two teams to predict the outcome</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="team1">Team 1</Label>
              <Select value={team1} onValueChange={setTeam1}>
                <SelectTrigger id="team1">
                  <SelectValue placeholder="Select team 1" />
                </SelectTrigger>
                <SelectContent>
                  {teams.map((team) => (
                    <SelectItem key={team.team} value={team.team}>
                      {team.team}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="team2">Team 2</Label>
              <Select value={team2} onValueChange={setTeam2}>
                <SelectTrigger id="team2">
                  <SelectValue placeholder="Select team 2" />
                </SelectTrigger>
                <SelectContent>
                  {teams.map((team) => (
                    <SelectItem key={team.team} value={team.team}>
                      {team.team}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="homeTeam">Home Team (Optional)</Label>
              <Select value={homeTeam} onValueChange={setHomeTeam}>
                <SelectTrigger id="homeTeam">
                  <SelectValue placeholder="Auto (Team 1)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Auto (Team 1)</SelectItem>
                  {team1 && (
                    <SelectItem key={team1} value={team1}>
                      {team1}
                    </SelectItem>
                  )}
                  {team2 && (
                    <SelectItem key={team2} value={team2}>
                      {team2}
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>

            {error && (
              <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                {error}
              </div>
            )}

            <Button onClick={handlePredict} disabled={loading} className="w-full">
              {loading ? 'Predicting...' : 'Get Prediction'}
            </Button>
          </CardContent>
        </Card>

        {prediction && (
          <Card>
            <CardHeader>
              <CardTitle>Prediction Results</CardTitle>
              <CardDescription>Model predictions for this matchup</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Matchup</h3>
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="text-center flex-1">
                    <p className="font-semibold">{prediction.homeTeam}</p>
                    <Badge variant="default" className="mt-2">
                      Home
                    </Badge>
                  </div>
                  <span className="mx-4 text-2xl font-bold">vs</span>
                  <div className="text-center flex-1">
                    <p className="font-semibold">{prediction.awayTeam}</p>
                    <Badge variant="outline" className="mt-2">
                      Away
                    </Badge>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Predicted Score</h3>
                <div className="text-center p-4 rounded-lg bg-primary/10">
                  <p className="text-3xl font-bold">{prediction.predictedScore}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Expected Total: {prediction.expectedTotal.toFixed(1)}
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Win Probabilities</h3>
                <div className="space-y-3">
                  <div className="p-3 rounded-lg border">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{prediction.homeTeam}</span>
                      <Badge variant="default">
                        {(prediction.homeWinProbability * 100).toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full"
                        style={{
                          width: `${prediction.homeWinProbability * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="p-3 rounded-lg border">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{prediction.awayTeam}</span>
                      <Badge variant="outline">
                        {(prediction.awayWinProbability * 100).toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full"
                        style={{
                          width: `${prediction.awayWinProbability * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">ELO Model</p>
                  <p className="text-sm">
                    Home: {(prediction.eloPrediction.homeWinProbability * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm">
                    Away: {(prediction.eloPrediction.awayWinProbability * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Poisson Model</p>
                  <p className="text-sm">
                    Home: {(prediction.poissonPrediction.homeWinProbability * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm">
                    Away: {(prediction.poissonPrediction.awayWinProbability * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

