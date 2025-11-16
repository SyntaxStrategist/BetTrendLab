'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useRefreshData } from '@/hooks/use-refresh-data';
import { RefreshCw } from 'lucide-react';

const navItems = [
  { href: '/', label: 'Home' },
  { href: '/rankings', label: 'Rankings' },
  { href: '/prediction', label: 'Prediction' },
  { href: '/value-bet', label: 'Value Bets' },
  { href: '/recommendations', label: 'Daily Recommendations' },
];

export function Navigation() {
  const pathname = usePathname();
  const { refreshData, isRefreshing } = useRefreshData();

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="text-xl font-bold">
            BetTrendLab
          </Link>
          <div className="flex items-center gap-2">
            <div className="flex space-x-1 overflow-x-auto">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'px-3 py-2 text-sm font-medium transition-colors rounded-md whitespace-nowrap',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )}
                  >
                    <span className="hidden sm:inline">{item.label}</span>
                    <span className="sm:hidden">
                      {item.label.split(' ')[0]}
                    </span>
                  </Link>
                );
              })}
            </div>
            <Button
              onClick={refreshData}
              disabled={isRefreshing}
              variant="outline"
              size="sm"
              className="ml-2"
            >
              <RefreshCw
                className={cn(
                  'h-4 w-4 mr-2',
                  isRefreshing && 'animate-spin'
                )}
              />
              <span className="hidden sm:inline">Refresh Data</span>
              <span className="sm:hidden">Refresh</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}

