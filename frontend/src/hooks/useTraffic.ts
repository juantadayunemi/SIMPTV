import { useState, useEffect } from 'react';
import { trafficService, TrafficAnalysis, TrafficStatistics, TrafficPrediction } from '../services/traffic.service';

interface TrafficState {
  analyses: TrafficAnalysis[];
  statistics: TrafficStatistics | null;
  isLoading: boolean;
  error: string | null;
}

export const useTraffic = () => {
  const [state, setState] = useState<TrafficState>({
    analyses: [],
    statistics: null,
    isLoading: false,
    error: null,
  });

  const fetchAnalyses = async (params?: {
    location?: string;
    status?: string;
    page?: number;
    limit?: number;
  }) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const analyses = await trafficService.getAnalyses(params);
      
      setState(prev => ({
        ...prev,
        analyses,
        isLoading: false,
      }));

      return analyses;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch traffic analyses';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const fetchStatistics = async (location?: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const statistics = await trafficService.getStatistics(location);
      
      setState(prev => ({
        ...prev,
        statistics,
        isLoading: false,
      }));

      return statistics;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch statistics';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const createAnalysis = async (location: string, videoPath?: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const analysis = await trafficService.createAnalysis({ location, videoPath });
      
      setState(prev => ({
        ...prev,
        analyses: [analysis, ...prev.analyses],
        isLoading: false,
      }));

      return analysis;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create analysis';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const uploadVideo = async (analysisId: string, videoFile: File) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const result = await trafficService.uploadVideo(analysisId, videoFile);
      
      // Update the analysis in the list
      setState(prev => ({
        ...prev,
        analyses: prev.analyses.map(analysis =>
          analysis.id === analysisId
            ? { ...analysis, videoPath: result.file_path }
            : analysis
        ),
        isLoading: false,
      }));

      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to upload video';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const analyzeVideo = async (analysisId: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const updatedAnalysis = await trafficService.analyzeVideo(analysisId);
      
      setState(prev => ({
        ...prev,
        analyses: prev.analyses.map(analysis =>
          analysis.id === analysisId ? updatedAnalysis : analysis
        ),
        isLoading: false,
      }));

      return updatedAnalysis;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to analyze video';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const deleteAnalysis = async (analysisId: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      await trafficService.deleteAnalysis(analysisId);
      
      setState(prev => ({
        ...prev,
        analyses: prev.analyses.filter(analysis => analysis.id !== analysisId),
        isLoading: false,
      }));
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete analysis';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  return {
    ...state,
    fetchAnalyses,
    fetchStatistics,
    createAnalysis,
    uploadVideo,
    analyzeVideo,
    deleteAnalysis,
    clearError,
  };
};

// Hook for traffic predictions
export const useTrafficPredictions = (location: string, hoursAhead: number = 24) => {
  const [predictions, setPredictions] = useState<TrafficPrediction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (location) {
      fetchPredictions();
    }
  }, [location, hoursAhead]);

  const fetchPredictions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await trafficService.getPredictions(location, hoursAhead);
      setPredictions(result.predictions);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to fetch predictions');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshPredictions = () => {
    fetchPredictions();
  };

  return {
    predictions,
    isLoading,
    error,
    refreshPredictions,
  };
};