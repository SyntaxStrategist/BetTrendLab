'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api, ValueBetsResponse, TeamRating } from '@/lib/api';
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

export default function ValueBetPage() {
  const [teams, setTeams] = useState<TeamRating[]>([]);
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [homeTeam, setHomeTeam] = useState('');
  const [odds1, setOdds1] = useState('');
  const [odds2, setOdds2] = useState('');
  const [analysis, setAnalysis] = useState<ValueBetsResponse | null>(null);
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

  const handleAnalyze = async () => {
    if (!team1 || !team2 || !odds1 || !odds2) {
      setError('Please fill in all fields');
      return;
    }

    const odds1Num = parseFloat(odds1);
    const odds2Num = parseFloat(odds2);

    if (isNaN(odds1Num) || isNaN(odds2Num)) {
      setError('Please enter valid odds (numbers)');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const result = await api.getValueBets(
        team1,
        team2,
        odds1Num,
        odds2Num,
        homeTeam || undefined
      );
      setAnalysis(result);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to analyze value bets. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const formatOdds = (odds: number) => {
    return odds > 0 ? `+${odds}` : odds.toString();
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Value Bet Analyzer</h1>
        <p className="text-muted-foreground text-lg">
          Compare model predictions with betting odds to find value opportunities
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Enter Matchup & Odds</CardTitle>
            <CardDescription>
              Use American odds format (e.g., -150 or +130)
            </CardDescription>
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
              <Label htmlFor="odds1">Team 1 Odds (American)</Label>
              <Input
                id="odds1"
                type="number"
                placeholder="-150 or +130"
                value={odds1}
                onChange={(e) => setOdds1(e.target.value)}
              />
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
              <Label htmlFor="odds2">Team 2 Odds (American)</Label>
              <Input
                id="odds2"
                type="number"
                placeholder="-150 or +130"
                value={odds2}
                onChange={(e) => setOdds2(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="homeTeam">Home Team (Optional)</Label>
              <Select value={homeTeam || "auto"} onValueChange={(value) => setHomeTeam(value === "auto" ? "" : value)}>
                <SelectTrigger id="homeTeam">
                  <SelectValue placeholder="Auto (Team 1)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto (Team 1)</SelectItem>
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

            <Button onClick={handleAnalyze} disabled={loading} className="w-full">
              {loading ? 'Analyzing...' : 'Analyze Value Bets'}
            </Button>
          </CardContent>
        </Card>

        {analysis && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Matchup</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="text-center flex-1">
                    <p className="font-semibold">{analysis.homeTeam}</p>
                    <Badge variant="default" className="mt-2">Home</Badge>
                  </div>
                  <span className="mx-4 text-2xl font-bold">vs</span>
                  <div className="text-center flex-1">
                    <p className="font-semibold">{analysis.awayTeam}</p>
                    <Badge variant="outline" className="mt-2">Away</Badge>
                  </div>
                </div>
                <p className="text-center mt-4 text-sm text-muted-foreground">
                  Expected Score: {analysis.expectedScore}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Home Team Analysis</CardTitle>
                <CardDescription>{analysis.homeAnalysis.team}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Odds</span>
                  <Badge variant="outline">{formatOdds(analysis.homeAnalysis.odds)}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Model Probability</span>
                  <span className="font-semibold">
                    {formatPercent(analysis.homeAnalysis.modelProbability)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Implied Probability</span>
                  <span className="font-semibold">
                    {formatPercent(analysis.homeAnalysis.impliedProbability)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Edge</span>
                  <Badge
                    variant={
                      analysis.homeAnalysis.edge > 0 ? 'default' : 'destructive'
                    }
                  >
                    {formatPercent(analysis.homeAnalysis.edge)}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Expected Value</span>
                  <Badge
                    variant={
                      analysis.homeAnalysis.expectedValue > 0 ? 'default' : 'destructive'
                    }
                  >
                    {formatPercent(analysis.homeAnalysis.expectedValue)}
                  </Badge>
                </div>
                <div className="pt-4 border-t">
                  {analysis.homeAnalysis.isValueBet ? (
                    <Badge className="w-full justify-center py-2" variant="default">
                      ✓ Value Bet Detected
                    </Badge>
                  ) : (
                    <Badge className="w-full justify-center py-2" variant="outline">
                      No Value Bet
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Away Team Analysis</CardTitle>
                <CardDescription>{analysis.awayAnalysis.team}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Odds</span>
                  <Badge variant="outline">{formatOdds(analysis.awayAnalysis.odds)}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Model Probability</span>
                  <span className="font-semibold">
                    {formatPercent(analysis.awayAnalysis.modelProbability)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Implied Probability</span>
                  <span className="font-semibold">
                    {formatPercent(analysis.awayAnalysis.impliedProbability)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Edge</span>
                  <Badge
                    variant={
                      analysis.awayAnalysis.edge > 0 ? 'default' : 'destructive'
                    }
                  >
                    {formatPercent(analysis.awayAnalysis.edge)}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Expected Value</span>
                  <Badge
                    variant={
                      analysis.awayAnalysis.expectedValue > 0 ? 'default' : 'destructive'
                    }
                  >
                    {formatPercent(analysis.awayAnalysis.expectedValue)}
                  </Badge>
                </div>
                <div className="pt-4 border-t">
                  {analysis.awayAnalysis.isValueBet ? (
                    <Badge className="w-full justify-center py-2" variant="default">
                      ✓ Value Bet Detected
                    </Badge>
                  ) : (
                    <Badge className="w-full justify-center py-2" variant="outline">
                      No Value Bet
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

