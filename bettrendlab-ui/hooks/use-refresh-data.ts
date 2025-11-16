'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export function useRefreshData() {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      toast.loading('Updating data...', { id: 'refresh' });
      
      // Call the update endpoint
      const result = await api.updateData();
      
      if (result.status === 'success') {
        toast.success(
          result.message || 'Data updated successfully',
          {
            id: 'refresh',
            description: result.games_processed
              ? `${result.games_processed} games processed, ${result.teams_updated} teams updated`
              : undefined,
          }
        );
        
        // Trigger a page refresh to reload all data
        // This will cause all pages to refetch their data on mount
        window.location.reload();
      } else if (result.status === 'partial') {
        toast.info(result.message || 'No new data available', { id: 'refresh' });
      } else {
        toast.error(result.message || 'Update failed', { id: 'refresh' });
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Failed to update data';
      toast.error(errorMessage, { id: 'refresh' });
    } finally {
      setIsRefreshing(false);
    }
  };

  return { refreshData, isRefreshing };
}

