'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api, RankingsResponse } from '@/lib/api';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

export default function RankingsPage() {
  const [rankings, setRankings] = useState<RankingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRankings = async () => {
      try {
        setLoading(true);
        const data = await api.getRankings();
        setRankings(data);
      } catch (err) {
        setError('Failed to load rankings. Please check your backend connection.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRankings();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Team Rankings</h1>
        <p className="text-muted-foreground text-lg">
          Complete ELO ratings for all NBA teams
        </p>
        {rankings?.updatedAt && (
          <p className="text-sm text-muted-foreground mt-2">
            Last updated: {new Date(rankings.updatedAt).toLocaleString()}
          </p>
        )}
      </div>

      {loading && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading rankings...</p>
        </div>
      )}

      {error && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
          </CardContent>
        </Card>
      )}

      {rankings && (
        <Card>
          <CardHeader>
            <CardTitle>ELO Rankings</CardTitle>
            <CardDescription>
              {rankings.rankings.length} teams ranked by ELO rating
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-20">Rank</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead className="text-right">ELO Rating</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rankings.rankings.map((item) => (
                    <TableRow key={item.team}>
                      <TableCell>
                        <Badge
                          variant={
                            item.rank <= 3
                              ? 'default'
                              : item.rank <= 10
                              ? 'secondary'
                              : 'outline'
                          }
                        >
                          #{item.rank}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium">{item.team}</TableCell>
                      <TableCell className="text-right">
                        <span className="font-semibold">
                          {item.eloRating.toFixed(2)}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

