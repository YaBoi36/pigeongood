import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { 
  Trophy, 
  Bird, 
  Upload, 
  Search, 
  Filter, 
  Plus, 
  Medal, 
  Timer, 
  MapPin,
  Calendar,
  Users,
  Target,
  BarChart3,
  Eye,
  Edit,
  Trash2,
  Home,
  Heart,
  ShoppingCart,
  Settings,
  Menu,
  X,
  Baby,
  Stethoscope,
  BookOpen,
  TrendingUp,
  Clock,
  CheckCircle
} from "lucide-react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { useToast } from "./hooks/use-toast";
import { Toaster } from "./components/ui/toaster";
import { Textarea } from "./components/ui/textarea";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

// Sidebar Navigation Component
const Sidebar = ({ activeTab, setActiveTab, isMobileOpen, setIsMobileOpen }) => {
  const menuItems = [
    { key: 'dashboard', label: 'Dashboard', icon: Home },
    { key: 'my-pigeons', label: 'My Pigeons', icon: Bird },
    { key: 'race-results', label: 'Race Results', icon: Trophy },
    { key: 'breeding', label: 'Breeding & Pairing', icon: Heart },
    { key: 'health', label: 'Health & Training', icon: Stethoscope },
    { key: 'sales', label: 'Sales & Transfers', icon: ShoppingCart },
    { key: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        isMobileOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Logo */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bird className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">PigeonPedigree</h1>
              <p className="text-sm text-gray-500">Racing Performance</p>
            </div>
          </div>
          {/* Mobile close button */}
          <button 
            className="lg:hidden"
            onClick={() => setIsMobileOpen(false)}
          >
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                onClick={() => {
                  setActiveTab(item.key);
                  setIsMobileOpen(false);
                }}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === item.key
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [dashboardStats, setDashboardStats] = useState({
    total_pigeons: 0,
    total_races: 0,
    total_results: 0,
    total_wins: 0,
    top_performers: []
  });
  const [raceResults, setRaceResults] = useState([]);

  useEffect(() => {
    fetchDashboardStats();
    fetchRaceResults();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard-stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const fetchRaceResults = async () => {
    try {
      const response = await axios.get(`${API}/race-results`);
      setRaceResults(response.data);
    } catch (error) {
      console.error('Error fetching race results:', error);
    }
  };

  const handleDeleteRaceResult = async (resultId) => {
    if (!window.confirm("Are you sure you want to delete this race result?")) return;
    
    try {
      await axios.delete(`${API}/race-results/${resultId}`);
      fetchRaceResults();
      fetchDashboardStats();
    } catch (error) {
      console.error('Error deleting race result:', error);
    }
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Track and analyze your pigeons' racing performance with detailed statistics and insights.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Pigeons</p>
                <p className="text-3xl font-bold text-blue-600">{dashboardStats.total_pigeons || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Bird className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">In your loft</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Races</p>
                <p className="text-3xl font-bold text-blue-600">{dashboardStats.total_races || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Trophy className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Across all categories</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Results</p>
                <p className="text-3xl font-bold text-green-600">{dashboardStats.total_results || 0}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Results recorded</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Wins</p>
                <p className="text-3xl font-bold text-yellow-600">{dashboardStats.total_wins || 0}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Medal className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">First place finishes</p>
          </CardContent>
        </Card>
      </div>

      {/* Top Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {dashboardStats.top_performers && dashboardStats.top_performers.slice(0, 3).map((performer, index) => (
          <Card key={performer.ring_number} className="relative overflow-hidden">
            <div className={`absolute top-0 left-0 w-full h-1 ${
              index === 0 ? 'bg-yellow-400' : index === 1 ? 'bg-gray-400' : 'bg-orange-400'
            }`}></div>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{performer.name}</CardTitle>
                <Badge variant="secondary" className={`${
                  index === 0 ? 'bg-yellow-100 text-yellow-800' : 
                  index === 1 ? 'bg-gray-100 text-gray-800' : 
                  'bg-orange-100 text-orange-800'
                }`}>
                  {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'} Top Performer
                </Badge>
              </div>
              <CardDescription>Ring: {performer.ring_number}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Races</span>
                  <span className="font-semibold">{performer.total_races}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Best Position</span>
                  <span className="font-semibold">{performer.best_position}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Avg Speed</span>
                  <span className="font-semibold">{performer.avg_speed} m/min</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Race Results */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Race Results</CardTitle>
          <CardDescription>{raceResults.length} results recorded</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {raceResults.slice(0, 10).map((result) => (
              <div key={result.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                    <Badge variant="outline" className="text-xs font-bold">
                      #{result.position}
                    </Badge>
                  </div>
                  <div>
                    <h3 className="font-semibold">{result.pigeon?.name || 'Unknown'}</h3>
                    <p className="text-sm text-gray-500">Ring: {result.ring_number}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-8 text-sm">
                  <div className="text-center">
                    <p className="font-semibold">{result.race?.race_name}</p>
                    <p className="text-gray-500">Race</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.race?.date}</p>
                    <p className="text-gray-500">Date</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.race?.total_pigeons || 0}</p>
                    <p className="text-gray-500">Pigeons</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{(result.distance / 1000).toFixed(1)}km</p>
                    <p className="text-gray-500">Distance</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.speed.toFixed(1)}</p>
                    <p className="text-gray-500">Speed</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.coefficient.toFixed(2)}</p>
                    <p className="text-gray-500">Coefficient</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeleteRaceResult(result.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Race Results Component 
const RaceResults = () => {
  const [raceResults, setRaceResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dashboardStats, setDashboardStats] = useState({});
  const [filters, setFilters] = useState({
    search: "",
    race: "",
    minPlace: "",
    maxPlace: "",
    dateFrom: "",
    dateTo: ""
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchRaceResults();
    fetchDashboardStats();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [raceResults, filters]);

  const applyFilters = () => {
    let filtered = [...raceResults];

    // Text search (name, ring number, race)
    if (filters.search) {
      filtered = filtered.filter(result => 
        (result.pigeon?.name?.toLowerCase().includes(filters.search.toLowerCase())) ||
        (result.ring_number?.toLowerCase().includes(filters.search.toLowerCase())) ||
        (result.race?.race_name?.toLowerCase().includes(filters.search.toLowerCase()))
      );
    }

    // Race filter
    if (filters.race) {
      filtered = filtered.filter(result => 
        result.race?.race_name?.toLowerCase().includes(filters.race.toLowerCase())
      );
    }

    // Place range filter
    if (filters.minPlace) {
      filtered = filtered.filter(result => result.position >= parseInt(filters.minPlace));
    }
    if (filters.maxPlace) {
      filtered = filtered.filter(result => result.position <= parseInt(filters.maxPlace));
    }

    // Date filters
    if (filters.dateFrom) {
      filtered = filtered.filter(result => result.race?.date >= filters.dateFrom);
    }
    if (filters.dateTo) {
      filtered = filtered.filter(result => result.race?.date <= filters.dateTo);
    }

    setFilteredResults(filtered);
  };

  const resetFilters = () => {
    setFilters({
      search: "",
      race: "",
      minPlace: "",
      maxPlace: "",
      dateFrom: "",
      dateTo: ""
    });
  };

  useEffect(() => {
    fetchRaceResults();
    fetchDashboardStats();
  }, []);

  const fetchRaceResults = async () => {
    try {
      const response = await axios.get(`${API}/race-results`);
      setRaceResults(response.data);
    } catch (error) {
      console.error('Error fetching race results:', error);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard-stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select a TXT file to upload",
        variant: "destructive",
      });
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload-race-results`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      toast({
        title: "Success!",
        description: `Processed ${response.data.races} races with ${response.data.results} results`,
      });

      setFile(null);
      fetchRaceResults();
      fetchDashboardStats();
    } catch (error) {
      toast({
        title: "Upload failed",
        description: error.response?.data?.detail || "Failed to process file",
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteRaceResult = async (resultId) => {
    if (!window.confirm("Are you sure you want to delete this race result?")) return;
    
    try {
      await axios.delete(`${API}/race-results/${resultId}`);
      toast({
        title: "Success!",
        description: "Race result deleted successfully",
      });
      fetchRaceResults();
      fetchDashboardStats();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete race result",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Race Results</h1>
          <p className="text-gray-500 mt-1">Track and analyze your pigeons' racing performance with detailed statistics and insights.</p>
        </div>
        
        <Dialog>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Upload className="w-4 h-4 mr-2" />
              Add New Result
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload Race Results</DialogTitle>
              <DialogDescription>
                Upload a TXT file containing race results to automatically parse and add results for your registered pigeons.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="file">Select TXT File</Label>
                <Input
                  id="file"
                  type="file"
                  accept=".txt"
                  onChange={(e) => setFile(e.target.files[0])}
                />
              </div>
              <Button 
                onClick={handleFileUpload} 
                disabled={uploading || !file}
                className="w-full"
              >
                {uploading ? 'Processing...' : 'Upload and Process'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filter Results</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="md:col-span-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  id="search"
                  placeholder="Name, ring number, race..."
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="race">Race</Label>
              <Input
                id="race"
                placeholder="Race name"
                value={filters.race}
                onChange={(e) => setFilters({...filters, race: e.target.value})}
              />
            </div>

            <div>
              <Label htmlFor="minPlace">Min Place</Label>
              <Input
                id="minPlace"
                type="number"
                placeholder="1"
                value={filters.minPlace}
                onChange={(e) => setFilters({...filters, minPlace: e.target.value})}
              />
            </div>

            <div>
              <Label htmlFor="maxPlace">Max Place</Label>
              <Input
                id="maxPlace"
                type="number"
                placeholder="100"
                value={filters.maxPlace}
                onChange={(e) => setFilters({...filters, maxPlace: e.target.value})}
              />
            </div>

            <div>
              <Label htmlFor="dateFrom">Date From</Label>
              <Input
                id="dateFrom"
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
              />
            </div>

            <div>
              <Label htmlFor="dateTo">Date To</Label>
              <Input
                id="dateTo"
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
              />
            </div>
            
            <div className="md:col-span-3 lg:col-span-6 flex items-end space-x-2">
              <Button variant="outline" onClick={resetFilters} className="flex-1">
                <X className="w-4 h-4 mr-2" />
                Clear Filters
              </Button>
              <div className="text-sm text-gray-500">
                Showing {filteredResults.length} of {raceResults.length} results
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Races</p>
                <p className="text-3xl font-bold text-blue-600">{dashboardStats.total_races || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Trophy className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Across all categories</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Results</p>
                <p className="text-3xl font-bold text-green-600">{dashboardStats.total_results || 0}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Results recorded</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Wins</p>
                <p className="text-3xl font-bold text-yellow-600">{dashboardStats.total_wins || 0}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Medal className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">First place finishes</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Win Rate</p>
                <p className="text-3xl font-bold text-purple-600">
                  {dashboardStats.total_results > 0 
                    ? `${((dashboardStats.total_wins / dashboardStats.total_results) * 100).toFixed(1)}%`
                    : '0%'}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Performance rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Race Results List */}
      <Card>
        <CardHeader>
          <CardTitle>Race Results</CardTitle>
          <CardDescription>{filteredResults.length} results found</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredResults.map((result) => (
              <div key={result.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                    <Badge variant="outline" className="text-xs font-bold">
                      #{result.position}
                    </Badge>
                  </div>
                  <div>
                    <h3 className="font-semibold">{result.pigeon?.name || 'Unknown'}</h3>
                    <p className="text-sm text-gray-500">Ring: {result.ring_number}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-8 text-sm">
                  <div className="text-center">
                    <p className="font-semibold">{result.race?.race_name}</p>
                    <p className="text-gray-500">Race</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.race?.date}</p>
                    <p className="text-gray-500">Date</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.race?.total_pigeons || 0}</p>
                    <p className="text-gray-500">Pigeons</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{(result.distance / 1000).toFixed(1)}km</p>
                    <p className="text-gray-500">Distance</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.speed.toFixed(1)}</p>
                    <p className="text-gray-500">Speed</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold">{result.coefficient.toFixed(2)}</p>
                    <p className="text-gray-500">Coefficient</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeleteRaceResult(result.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// My Pigeons Component  
const MyPigeons = () => {
  const [pigeons, setPigeons] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [addPigeonOpen, setAddPigeonOpen] = useState(false);
  const [editPigeonOpen, setEditPigeonOpen] = useState(false);
  const [currentPigeon, setCurrentPigeon] = useState(null);
  const { toast } = useToast();

  const [newPigeon, setNewPigeon] = useState({
    ring_number: "",
    name: "",
    country: "",  // Empty by default, must be selected
    gender: "",
    color: "",
    breeder: "",
    loft: "",  // New loft field
    sire_ring: "",
    dam_ring: ""
  });

  useEffect(() => {
    fetchPigeons();
  }, [searchTerm]);

  const fetchPigeons = async () => {
    try {
      const params = searchTerm ? { search: searchTerm } : {};
      const response = await axios.get(`${API}/pigeons`, { params });
      setPigeons(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching pigeons:', error);
      setLoading(false);
    }
  };

  const handleAddPigeon = async () => {
    // Validate required fields
    if (!newPigeon.country) {
      toast({
        title: "Country Required",
        description: "Please select a country before adding the pigeon.",
        variant: "destructive",
      });
      return;
    }

    if (!newPigeon.ring_number) {
      toast({
        title: "Ring number required",
        description: "Please enter a ring number.",
        variant: "destructive",
      });
      return;
    }

    if (!newPigeon.gender) {
      toast({
        title: "Gender required",
        description: "Please select a gender.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Construct full ring number
      const fullRingNumber = `${newPigeon.country}${newPigeon.ring_number}`;
      const pigeonData = {
        ...newPigeon,
        ring_number: fullRingNumber
      };

      await axios.post(`${API}/pigeons`, pigeonData);
      
      toast({
        title: "Success!",
        description: "Pigeon added successfully",
      });
      
      setNewPigeon({
        ring_number: "",
        name: "",
        country: "",
        gender: "",
        color: "",
        breeder: "",
        loft: "",  // Reset loft field
        sire_ring: "",
        dam_ring: ""
      });
      setAddPigeonOpen(false);
      fetchPigeons();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add pigeon",
        variant: "destructive",
      });
    }
  };

  const handleDeletePigeon = async (pigeonId) => {
    if (!window.confirm("Are you sure you want to delete this pigeon? This will also delete all associated race results.")) return;

    try {
      await axios.delete(`${API}/pigeons/${pigeonId}`);
      toast({
        title: "Success!",
        description: "Pigeon and associated race results deleted successfully",
      });
      fetchPigeons();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete pigeon",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Pigeons</h1>
          <p className="text-gray-500 mt-1">You currently have {pigeons.length} pigeons registered. Your plan allows up to 100 pigeons.</p>
        </div>
        
        <Dialog open={addPigeonOpen} onOpenChange={setAddPigeonOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Add New Pigeon
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Add New Pigeon</DialogTitle>
              <DialogDescription>Register a new pigeon in your collection</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="ring_number">Ring Number (numbers only) *</Label>
                <Input 
                  id="ring_number"
                  type="number"
                  value={newPigeon.ring_number}
                  onChange={(e) => setNewPigeon({...newPigeon, ring_number: e.target.value})}
                  placeholder="501516325"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  {newPigeon.country && newPigeon.ring_number 
                    ? `Full ring number: ${newPigeon.country}${newPigeon.ring_number}` 
                    : "Select country and enter numbers"}
                </p>
              </div>
              <div>
                <Label htmlFor="name">Name</Label>
                <Input 
                  id="name"
                  value={newPigeon.name}
                  onChange={(e) => setNewPigeon({...newPigeon, name: e.target.value})}
                  placeholder="Golden Sky"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="country">Country *</Label>
                  <Select onValueChange={(value) => setNewPigeon({...newPigeon, country: value})} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Country *" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="BE">Belgium (BE)</SelectItem>
                      <SelectItem value="NL">Netherlands (NL)</SelectItem>
                      <SelectItem value="DE">Germany (DE)</SelectItem>
                      <SelectItem value="FR">France (FR)</SelectItem>
                      <SelectItem value="GB">United Kingdom (GB)</SelectItem>
                      <SelectItem value="DV">DV (Special)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="gender">Gender *</Label>
                  <Select onValueChange={(value) => setNewPigeon({...newPigeon, gender: value})} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Gender *" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Male">Male</SelectItem>
                      <SelectItem value="Female">Female</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="color">Color</Label>
                  <Input 
                    id="color"
                    value={newPigeon.color}
                    onChange={(e) => setNewPigeon({...newPigeon, color: e.target.value})}
                    placeholder="Blue"
                  />
                </div>
                <div>
                  <Label htmlFor="breeder">Breeder</Label>
                  <Input 
                    id="breeder"
                    value={newPigeon.breeder}
                    onChange={(e) => setNewPigeon({...newPigeon, breeder: e.target.value})}
                    placeholder="John Doe"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="loft">Loft (Optional)</Label>
                <Input 
                  id="loft"
                  value={newPigeon.loft}
                  onChange={(e) => setNewPigeon({...newPigeon, loft: e.target.value})}
                  placeholder="Main Loft, Training Facility, etc."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="sire_ring">Sire Ring</Label>
                  <Input 
                    id="sire_ring"
                    value={newPigeon.sire_ring}
                    onChange={(e) => setNewPigeon({...newPigeon, sire_ring: e.target.value})}
                    placeholder="Optional"
                  />
                </div>
                <div>
                  <Label htmlFor="dam_ring">Dam Ring</Label>
                  <Input 
                    id="dam_ring"
                    value={newPigeon.dam_ring}
                    onChange={(e) => setNewPigeon({...newPigeon, dam_ring: e.target.value})}
                    placeholder="Optional"
                  />
                </div>
              </div>
              <Button onClick={handleAddPigeon} className="w-full">
                Add Pigeon
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search Bar */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search by name, ring number, color, or breeder..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Genders" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Genders</SelectItem>
            <SelectItem value="male">Male</SelectItem>
            <SelectItem value="female">Female</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          Advanced Filters
        </Button>
      </div>

      {/* Plan Usage Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Plan Usage</p>
                <p className="text-2xl font-bold text-blue-600">{pigeons.length}/100</p>
                <p className="text-sm text-gray-500">99 slots remaining</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Bird className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Active Birds</p>
                <p className="text-2xl font-bold text-green-600">{pigeons.length}</p>
                <p className="text-sm text-gray-500">Currently in loft</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Plus className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Recent Additions</p>
                <p className="text-2xl font-bold text-purple-600">2</p>
                <p className="text-sm text-gray-500">This month</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pigeons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pigeons.map((pigeon) => (
          <Card key={pigeon.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Bird className="w-6 h-6 text-blue-600" />
                </div>
                <Badge variant={pigeon.gender === 'Male' ? 'default' : 'secondary'}>
                  {pigeon.gender}
                </Badge>
              </div>
              <div>
                <CardTitle className="text-lg">{pigeon.name || 'Unnamed'}</CardTitle>
                <CardDescription>{pigeon.ring_number}</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Country</span>
                  <p className="font-semibold">{pigeon.country}</p>
                </div>
                <div>
                  <span className="text-gray-600">Gender</span>
                  <p className="font-semibold">{pigeon.gender}</p>
                </div>
                <div>
                  <span className="text-gray-600">Color</span>
                  <p className="font-semibold">{pigeon.color || '-'}</p>
                </div>
                <div>
                  <span className="text-gray-600">Breeder</span>
                  <p className="font-semibold">{pigeon.breeder || '-'}</p>
                </div>
                {pigeon.loft && (
                  <div className="col-span-2">
                    <span className="text-gray-600">Loft</span>
                    <p className="font-semibold">{pigeon.loft}</p>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-between pt-4 border-t">
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4 mr-1" />
                    View Profile
                  </Button>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeletePigeon(pigeon.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Breeding & Pairing Component
const BreedingPairing = () => {
  const [pigeons, setPigeons] = useState([]);
  const [pairings, setPairings] = useState([]);
  const [addPairingOpen, setAddPairingOpen] = useState(false);
  const [addResultOpen, setAddResultOpen] = useState(false);
  const [selectedPairing, setSelectedPairing] = useState(null);
  const [newPairing, setNewPairing] = useState({
    sire_id: "",
    dam_id: "",
    expected_hatch_date: "",
    notes: ""
  });
  const [newResult, setNewResult] = useState({
    ring_number: "",
    name: "",
    country: "NL",
    gender: "",
    color: "",
    breeder: ""
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchPigeons();
    fetchPairings();
  }, []);

  const fetchPigeons = async () => {
    try {
      const response = await axios.get(`${API}/pigeons`);
      setPigeons(response.data);
    } catch (error) {
      console.error('Error fetching pigeons:', error);
    }
  };

  const fetchPairings = async () => {
    try {
      const response = await axios.get(`${API}/pairings`);
      setPairings(response.data);
    } catch (error) {
      console.error('Error fetching pairings:', error);
    }
  };

  const handleAddPairing = async () => {
    if (!newPairing.sire_id || !newPairing.dam_id) {
      toast({
        title: "Missing Information",
        description: "Please select both sire and dam",
        variant: "destructive",
      });
      return;
    }

    if (newPairing.sire_id === newPairing.dam_id) {
      toast({
        title: "Invalid Pairing",
        description: "Sire and dam cannot be the same pigeon",
        variant: "destructive",
      });
      return;
    }

    try {
      await axios.post(`${API}/pairings`, newPairing);
      toast({
        title: "Success!",
        description: "Pairing recorded successfully",
      });
      
      setNewPairing({
        sire_id: "",
        dam_id: "",
        expected_hatch_date: "",
        notes: ""
      });
      setAddPairingOpen(false);
      fetchPairings();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to record pairing",
        variant: "destructive",
      });
    }
  };

  const handleAddResult = async () => {
    if (!newResult.ring_number) {
      toast({
        title: "Ring Number Required",
        description: "Please enter a ring number for the new pigeon",
        variant: "destructive",
      });
      return;
    }

    try {
      await axios.post(`${API}/pairings/${selectedPairing.id}/result`, newResult);
      toast({
        title: "Success!",
        description: "New pigeon created successfully from pairing",
      });
      
      setNewResult({
        ring_number: "",
        name: "",
        country: "NL",
        gender: "",
        color: "",
        breeder: ""
      });
      setAddResultOpen(false);
      setSelectedPairing(null);
      fetchPigeons();
      fetchPairings();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create pigeon from pairing",
        variant: "destructive",
      });
    }
  };

  const malePigeons = pigeons.filter(p => p.gender === 'Male');
  const femalePigeons = pigeons.filter(p => p.gender === 'Female');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Breeding & Pairing</h1>
          <p className="text-gray-500 mt-1">Manage breeding pairs and track breeding history</p>
        </div>
        
        <Dialog open={addPairingOpen} onOpenChange={setAddPairingOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Heart className="w-4 h-4 mr-2" />
              Create New Pairing
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create New Pairing</DialogTitle>
              <DialogDescription>Select sire and dam for breeding</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="sire">Sire (Father) *</Label>
                <Select onValueChange={(value) => setNewPairing({...newPairing, sire_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Sire" />
                  </SelectTrigger>
                  <SelectContent>
                    {malePigeons.map((pigeon) => (
                      <SelectItem key={pigeon.id} value={pigeon.id}>
                        {pigeon.name || 'Unnamed'} - {pigeon.ring_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="dam">Dam (Mother) *</Label>  
                <Select onValueChange={(value) => setNewPairing({...newPairing, dam_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Dam" />
                  </SelectTrigger>
                  <SelectContent>
                    {femalePigeons.map((pigeon) => (
                      <SelectItem key={pigeon.id} value={pigeon.id}>
                        {pigeon.name || 'Unnamed'} - {pigeon.ring_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="expected_hatch_date">Expected Hatch Date</Label>
                <Input 
                  id="expected_hatch_date"
                  type="date"
                  value={newPairing.expected_hatch_date}
                  onChange={(e) => setNewPairing({...newPairing, expected_hatch_date: e.target.value})}
                />
              </div>

              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea 
                  id="notes"
                  value={newPairing.notes}
                  onChange={(e) => setNewPairing({...newPairing, notes: e.target.value})}
                  placeholder="Any additional notes about this pairing..."
                />
              </div>

              <Button onClick={handleAddPairing} className="w-full">
                Create Pairing
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
                <Heart className="w-6 h-6 text-pink-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Active Pairings</p>
                <p className="text-2xl font-bold text-pink-600">{pairings.length}</p>
                <p className="text-sm text-gray-500">Current breeding pairs</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Breeding Stock</p>
                <p className="text-2xl font-bold text-blue-600">{malePigeons.length + femalePigeons.length}</p>
                <p className="text-sm text-gray-500">{malePigeons.length} males, {femalePigeons.length} females</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Baby className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Expected Hatchings</p>
                <p className="text-2xl font-bold text-green-600">0</p>
                <p className="text-sm text-gray-500">This month</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Available Breeding Stock */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Male Pigeons */}
        <Card>
          <CardHeader>
            <CardTitle>Available Sires (Males)</CardTitle>
            <CardDescription>{malePigeons.length} male pigeons available for breeding</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {malePigeons.slice(0, 5).map((pigeon) => (
                <div key={pigeon.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Bird className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-semibold">{pigeon.name || 'Unnamed'}</p>
                      <p className="text-sm text-gray-500">{pigeon.ring_number}</p>
                    </div>
                  </div>
                  <Badge variant="default">Male</Badge>
                </div>
              ))}
              {malePigeons.length > 5 && (
                <p className="text-sm text-gray-500 text-center">+{malePigeons.length - 5} more males</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Female Pigeons */}
        <Card>
          <CardHeader>
            <CardTitle>Available Dams (Females)</CardTitle>
            <CardDescription>{femalePigeons.length} female pigeons available for breeding</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {femalePigeons.slice(0, 5).map((pigeon) => (
                <div key={pigeon.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-pink-100 rounded-full flex items-center justify-center">
                      <Bird className="w-4 h-4 text-pink-600" />
                    </div>
                    <div>
                      <p className="font-semibold">{pigeon.name || 'Unnamed'}</p>
                      <p className="text-sm text-gray-500">{pigeon.ring_number}</p>
                    </div>
                  </div>
                  <Badge variant="secondary">Female</Badge>
                </div>
              ))}
              {femalePigeons.length > 5 && (
                <p className="text-sm text-gray-500 text-center">+{femalePigeons.length - 5} more females</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Pairings */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Pairings</CardTitle>
          <CardDescription>History of breeding pairs and their outcomes</CardDescription>
        </CardHeader>
        <CardContent>
          {pairings.length === 0 ? (
            <div className="text-center py-8">
              <Heart className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No pairings recorded yet</p>
              <p className="text-sm text-gray-400">Create your first breeding pair to get started</p>
            </div>
          ) : (
            <div className="space-y-4">
              {pairings.map((pairing) => {
                const sire = pigeons.find(p => p.id === pairing.sire_id);
                const dam = pigeons.find(p => p.id === pairing.dam_id);
                return (
                  <div key={pairing.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                        <Heart className="w-6 h-6 text-pink-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold">
                          {sire?.name || 'Unknown'} × {dam?.name || 'Unknown'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {sire?.ring_number} × {dam?.ring_number}
                        </p>
                        {pairing.expected_hatch_date && (
                          <p className="text-xs text-gray-400">Expected: {pairing.expected_hatch_date}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-green-600">
                        {pairing.status}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedPairing(pairing);
                          setAddResultOpen(true);
                        }}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Result
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Result Dialog */}
      <Dialog open={addResultOpen} onOpenChange={setAddResultOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Pairing Result</DialogTitle>
            <DialogDescription>
              Create a new pigeon from the breeding pair
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="result_ring_number">Ring Number *</Label>
              <Input 
                id="result_ring_number"
                value={newResult.ring_number}
                onChange={(e) => setNewResult({...newResult, ring_number: e.target.value})}
                placeholder="501123456"
                required
              />
            </div>

            <div>
              <Label htmlFor="result_name">Name (Optional)</Label>
              <Input 
                id="result_name"
                value={newResult.name}
                onChange={(e) => setNewResult({...newResult, name: e.target.value})}
                placeholder="Young Champion"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="result_country">Country (Optional)</Label>
                <Select onValueChange={(value) => setNewResult({...newResult, country: value})} defaultValue="NL">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="BE">Belgium (BE)</SelectItem>
                    <SelectItem value="NL">Netherlands (NL)</SelectItem>
                    <SelectItem value="DE">Germany (DE)</SelectItem>
                    <SelectItem value="FR">France (FR)</SelectItem>
                    <SelectItem value="GB">United Kingdom (GB)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="result_gender">Gender (Optional)</Label>
                <Select onValueChange={(value) => setNewResult({...newResult, gender: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Male">Male</SelectItem>
                    <SelectItem value="Female">Female</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="result_color">Color (Optional)</Label>
                <Input 
                  id="result_color"
                  value={newResult.color}
                  onChange={(e) => setNewResult({...newResult, color: e.target.value})}
                  placeholder="Blue"
                />
              </div>
              <div>
                <Label htmlFor="result_breeder">Breeder (Optional)</Label>
                <Input 
                  id="result_breeder"
                  value={newResult.breeder}
                  onChange={(e) => setNewResult({...newResult, breeder: e.target.value})}
                  placeholder="Your name"
                />
              </div>
            </div>

            <Button onClick={handleAddResult} className="w-full">
              Create Pigeon from Pairing
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Health & Training Component
const HealthTraining = () => {
  const [pigeons, setPigeons] = useState([]);
  const [healthLogs, setHealthLogs] = useState([]);
  const [loftLogs, setLoftLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('health');
  const [addLogOpen, setAddLogOpen] = useState(false);
  const [logMode, setLogMode] = useState('individual'); // 'individual' or 'loft'
  const [filters, setFilters] = useState({
    search: "",
    pigeon: "",
    loft: "",
    type: "",
    dateFrom: "",
    dateTo: ""
  });
  const [newLog, setNewLog] = useState({
    pigeon_id: "",
    type: "health",
    title: "",
    description: "",
    date: new Date().toISOString().split('T')[0],
    reminder_date: ""
  });
  const [newLoftLog, setNewLoftLog] = useState({
    loft_name: "",
    type: "health",
    title: "",
    description: "",
    date: new Date().toISOString().split('T')[0],
    reminder_date: ""
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchPigeons();
    fetchHealthLogs();
    fetchLoftLogs();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [healthLogs, loftLogs, filters, activeTab]);

  const applyFilters = () => {
    // Combine individual and loft logs
    let allLogs = [
      ...healthLogs.filter(log => log.type === activeTab),
      ...loftLogs.filter(log => log.type === activeTab).map(log => ({...log, isLoftLog: true}))
    ];

    // Search filter
    if (filters.search) {
      allLogs = allLogs.filter(log => 
        log.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        (log.description && log.description.toLowerCase().includes(filters.search.toLowerCase()))
      );
    }

    // Pigeon filter (only for individual logs)
    if (filters.pigeon) {
      allLogs = allLogs.filter(log => 
        log.isLoftLog || log.pigeon_id === filters.pigeon
      );
    }

    // Loft filter (only for loft logs)
    if (filters.loft) {
      allLogs = allLogs.filter(log => 
        !log.isLoftLog || log.loft_name.toLowerCase().includes(filters.loft.toLowerCase())
      );
    }

    // Date filters
    if (filters.dateFrom) {
      allLogs = allLogs.filter(log => log.date >= filters.dateFrom);
    }
    if (filters.dateTo) {
      allLogs = allLogs.filter(log => log.date <= filters.dateTo);
    }

    // Sort by date
    allLogs.sort((a, b) => new Date(b.date) - new Date(a.date));

    setFilteredLogs(allLogs);
  };

  const resetFilters = () => {
    setFilters({
      search: "",
      pigeon: "",
      loft: "",
      type: "",
      dateFrom: "",
      dateTo: ""
    });
  };

  const fetchPigeons = async () => {
    try {
      const response = await axios.get(`${API}/pigeons`);
      setPigeons(response.data);
    } catch (error) {
      console.error('Error fetching pigeons:', error);
    }
  };

  const fetchHealthLogs = async () => {
    try {
      const response = await axios.get(`${API}/health-logs`);
      setHealthLogs(response.data);
    } catch (error) {
      console.error('Error fetching health logs:', error);
    }
  };

  const fetchLoftLogs = async () => {
    try {
      const response = await axios.get(`${API}/loft-logs`);
      setLoftLogs(response.data);
    } catch (error) {
      console.error('Error fetching loft logs:', error);
    }
  };

  const handleAddLog = async () => {
    if (logMode === 'individual') {
      if (!newLog.pigeon_id || !newLog.title) {
        toast({
          title: "Missing Information",
          description: "Please select a pigeon and enter a title",
          variant: "destructive",
        });
        return;
      }

      try {
        await axios.post(`${API}/health-logs`, newLog);
        toast({
          title: "Success!",
          description: "Individual log entry added successfully",
        });
        
        setNewLog({
          pigeon_id: "",
          type: "health",
          title: "",
          description: "",
          date: new Date().toISOString().split('T')[0],
          reminder_date: ""
        });
        setAddLogOpen(false);
        fetchHealthLogs();
      } catch (error) {
        toast({
          title: "Error",
          description: error.response?.data?.detail || "Failed to add log entry",
          variant: "destructive",
        });
      }
    } else {
      if (!newLoftLog.loft_name || !newLoftLog.title) {
        toast({
          title: "Missing Information",
          description: "Please enter a loft name and title",
          variant: "destructive",
        });
        return;
      }

      try {
        await axios.post(`${API}/loft-logs`, newLoftLog);
        toast({
          title: "Success!",
          description: "Loft log entry added successfully",
        });
        
        setNewLoftLog({
          loft_name: "",
          type: "health",
          title: "",
          description: "",
          date: new Date().toISOString().split('T')[0],
          reminder_date: ""
        });
        setAddLogOpen(false);
        fetchLoftLogs();
      } catch (error) {
        toast({
          title: "Error",
          description: error.response?.data?.detail || "Failed to add loft log entry",
          variant: "destructive",
        });
      }
    }
  };

  const handleDeleteLog = async (log) => {
    if (!window.confirm(`Are you sure you want to delete this ${log.isLoftLog ? 'loft' : 'individual'} log entry?`)) return;

    try {
      const endpoint = log.isLoftLog ? 'loft-logs' : 'health-logs';
      await axios.delete(`${API}/${endpoint}/${log.id}`);
      toast({
        title: "Success!",
        description: "Log entry deleted successfully",
      });
      if (log.isLoftLog) {
        fetchLoftLogs();
      } else {
        fetchHealthLogs();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete log entry",
        variant: "destructive",
      });
    }
  };

  // Get unique loft names from pigeons
  const loftNames = [...new Set(pigeons.map(p => p.breeder).filter(Boolean))];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Health & Training</h1>
          <p className="text-gray-500 mt-1">Track health records, training sessions, and diet plans for your pigeons</p>
        </div>
        
        <Dialog open={addLogOpen} onOpenChange={setAddLogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Add Log Entry
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Add New Log Entry</DialogTitle>
              <DialogDescription>Record health, training, or diet information</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Entry Type</Label>
                <div className="flex space-x-4 mt-2">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      value="individual"
                      checked={logMode === 'individual'}
                      onChange={(e) => setLogMode(e.target.value)}
                      className="text-blue-600"
                    />
                    <span>Individual Pigeon</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      value="loft"
                      checked={logMode === 'loft'}
                      onChange={(e) => setLogMode(e.target.value)}
                      className="text-blue-600"
                    />
                    <span>Entire Loft</span>
                  </label>
                </div>
              </div>

              {logMode === 'individual' ? (
                <div>
                  <Label htmlFor="pigeon">Select Pigeon *</Label>
                  <Select onValueChange={(value) => setNewLog({...newLog, pigeon_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Pigeon" />
                    </SelectTrigger>
                    <SelectContent>
                      {pigeons.map((pigeon) => (
                        <SelectItem key={pigeon.id} value={pigeon.id}>
                          {pigeon.name || 'Unnamed'} - {pigeon.ring_number}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ) : (
                <div>
                  <Label htmlFor="loft_name">Loft/Breeder Name *</Label>
                  <Input 
                    id="loft_name"
                    value={newLoftLog.loft_name}
                    onChange={(e) => setNewLoftLog({...newLoftLog, loft_name: e.target.value})}
                    placeholder="Enter loft or breeder name"
                  />
                </div>
              )}

              <div>
                <Label htmlFor="type">Log Type *</Label>
                <Select 
                  onValueChange={(value) => {
                    if (logMode === 'individual') {
                      setNewLog({...newLog, type: value});
                    } else {
                      setNewLoftLog({...newLoftLog, type: value});
                    }
                  }} 
                  defaultValue="health"
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="health">Health Record</SelectItem>
                    <SelectItem value="training">Training Session</SelectItem>
                    <SelectItem value="diet">Diet Plan</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="title">Title *</Label>
                <Input 
                  id="title"
                  value={logMode === 'individual' ? newLog.title : newLoftLog.title}
                  onChange={(e) => {
                    if (logMode === 'individual') {
                      setNewLog({...newLog, title: e.target.value});
                    } else {
                      setNewLoftLog({...newLoftLog, title: e.target.value});
                    }
                  }}
                  placeholder="e.g., Vaccination, Training Flight, Diet Change"
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea 
                  id="description"
                  value={logMode === 'individual' ? newLog.description : newLoftLog.description}
                  onChange={(e) => {
                    if (logMode === 'individual') {
                      setNewLog({...newLog, description: e.target.value});
                    } else {
                      setNewLoftLog({...newLoftLog, description: e.target.value});
                    }
                  }}
                  placeholder="Additional details..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="date">Date *</Label>
                  <Input 
                    id="date"
                    type="date"
                    value={logMode === 'individual' ? newLog.date : newLoftLog.date}
                    onChange={(e) => {
                      if (logMode === 'individual') {
                        setNewLog({...newLog, date: e.target.value});
                      } else {
                        setNewLoftLog({...newLoftLog, date: e.target.value});
                      }
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="reminder_date">Reminder Date</Label>
                  <Input 
                    id="reminder_date"
                    type="date"
                    value={logMode === 'individual' ? newLog.reminder_date : newLoftLog.reminder_date}
                    onChange={(e) => {
                      if (logMode === 'individual') {
                        setNewLog({...newLog, reminder_date: e.target.value});
                      } else {
                        setNewLoftLog({...newLoftLog, reminder_date: e.target.value});
                      }
                    }}
                  />
                </div>
              </div>

              <Button onClick={handleAddLog} className="w-full">
                Add {logMode === 'individual' ? 'Individual' : 'Loft'} Log Entry
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <Stethoscope className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Health Records</p>
                <p className="text-2xl font-bold text-red-600">
                  {healthLogs.filter(log => log.type === 'health').length + loftLogs.filter(log => log.type === 'health').length}
                </p>
                <p className="text-sm text-gray-500">Individual + Loft entries</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Training Sessions</p>
                <p className="text-2xl font-bold text-blue-600">
                  {healthLogs.filter(log => log.type === 'training').length + loftLogs.filter(log => log.type === 'training').length}
                </p>
                <p className="text-sm text-gray-500">Individual + Loft sessions</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Diet Plans</p>
                <p className="text-2xl font-bold text-orange-600">
                  {healthLogs.filter(log => log.type === 'diet').length + loftLogs.filter(log => log.type === 'diet').length}
                </p>
                <p className="text-sm text-gray-500">Individual + Loft plans</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filter Log Entries</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div>
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  id="search"
                  placeholder="Title or description..."
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="pigeon_filter">Individual Pigeon</Label>
              <Select onValueChange={(value) => setFilters({...filters, pigeon: value === "all" ? "" : value})}>
                <SelectTrigger>
                  <SelectValue placeholder="All Individual" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Individual</SelectItem>
                  {pigeons.map((pigeon) => (
                    <SelectItem key={pigeon.id} value={pigeon.id}>
                      {pigeon.name || 'Unnamed'} - {pigeon.ring_number}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="loft_filter">Loft/Breeder</Label>
              <Select onValueChange={(value) => setFilters({...filters, loft: value === "all" ? "" : value})}>
                <SelectTrigger>
                  <SelectValue placeholder="All Lofts" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Lofts</SelectItem>
                  {loftNames.map((loft) => (
                    <SelectItem key={loft} value={loft}>
                      {loft}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="dateFrom">Date From</Label>
              <Input
                id="dateFrom"
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
              />
            </div>

            <div>
              <Label htmlFor="dateTo">Date To</Label>
              <Input
                id="dateTo"
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
              />
            </div>
            
            <div className="flex items-end">
              <Button variant="outline" onClick={resetFilters} className="w-full">
                <X className="w-4 h-4 mr-2" />
                Clear
              </Button>
            </div>
          </div>
          <div className="text-sm text-gray-500 mt-2">
            Showing {filteredLogs.length} entries (Individual: {filteredLogs.filter(l => !l.isLoftLog).length}, Loft: {filteredLogs.filter(l => l.isLoftLog).length})
          </div>
        </CardContent>
      </Card>

      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="health">Health Records</TabsTrigger>
          <TabsTrigger value="training">Training Sessions</TabsTrigger>
          <TabsTrigger value="diet">Diet Plans</TabsTrigger>
        </TabsList>

        <TabsContent value="health" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Health Records</CardTitle>
              <CardDescription>Track vaccinations, treatments, and medical history</CardDescription>
            </CardHeader>
            <CardContent>
              {filteredLogs.length === 0 ? (
                <div className="text-center py-8">
                  <Stethoscope className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No health records yet</p>
                  <p className="text-sm text-gray-400">Add your first health record to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredLogs.map((log) => {
                    const pigeon = log.isLoftLog ? null : pigeons.find(p => p.id === log.pigeon_id);
                    return (
                      <div key={`${log.isLoftLog ? 'loft' : 'individual'}-${log.id}`} className="flex items-start justify-between p-4 border rounded-lg">
                        <div className="flex items-start space-x-4">
                          <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                            <Stethoscope className="w-5 h-5 text-red-600" />
                          </div>
                          <div>
                            <div className="flex items-center space-x-2">
                              <h3 className="font-semibold">{log.title}</h3>
                              <Badge variant={log.isLoftLog ? "default" : "outline"} className="text-xs">
                                {log.isLoftLog ? 'Loft' : 'Individual'}
                              </Badge>
                            </div>
                            {log.isLoftLog ? (
                              <p className="text-sm text-gray-600">Loft: {log.loft_name}</p>
                            ) : (
                              <p className="text-sm text-gray-600">{pigeon?.name || 'Unknown'} - {pigeon?.ring_number}</p>
                            )}
                            <p className="text-sm text-gray-500">{log.date}</p>
                            {log.description && (
                              <p className="text-sm text-gray-600 mt-1">{log.description}</p>
                            )}
                            {log.reminder_date && (
                              <p className="text-xs text-orange-600 mt-1">Reminder: {log.reminder_date}</p>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteLog(log)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="training" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Training Sessions</CardTitle>
              <CardDescription>Log training flights, distances, and performance notes</CardDescription>
            </CardHeader>
            <CardContent>
              {filteredLogs.length === 0 ? (
                <div className="text-center py-8">
                  <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No training sessions recorded</p>
                  <p className="text-sm text-gray-400">Start logging training sessions to track progress</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredLogs.map((log) => {
                    const pigeon = log.isLoftLog ? null : pigeons.find(p => p.id === log.pigeon_id);
                    return (
                      <div key={`${log.isLoftLog ? 'loft' : 'individual'}-${log.id}`} className="flex items-start justify-between p-4 border rounded-lg">
                        <div className="flex items-start space-x-4">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <TrendingUp className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <div className="flex items-center space-x-2">
                              <h3 className="font-semibold">{log.title}</h3>
                              <Badge variant={log.isLoftLog ? "default" : "outline"} className="text-xs">
                                {log.isLoftLog ? 'Loft' : 'Individual'}
                              </Badge>
                            </div>
                            {log.isLoftLog ? (
                              <p className="text-sm text-gray-600">Loft: {log.loft_name}</p>
                            ) : (
                              <p className="text-sm text-gray-600">{pigeon?.name || 'Unknown'} - {pigeon?.ring_number}</p>
                            )}
                            <p className="text-sm text-gray-500">{log.date}</p>
                            {log.description && (
                              <p className="text-sm text-gray-600 mt-1">{log.description}</p>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteLog(log)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="diet" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Diet Plans</CardTitle>
              <CardDescription>Manage feeding schedules and nutritional information</CardDescription>
            </CardHeader>
            <CardContent>
              {filteredLogs.length === 0 ? (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No diet plans recorded</p>
                  <p className="text-sm text-gray-400">Create diet plans to optimize nutrition</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredLogs.map((log) => {
                    const pigeon = log.isLoftLog ? null : pigeons.find(p => p.id === log.pigeon_id);
                    return (
                      <div key={`${log.isLoftLog ? 'loft' : 'individual'}-${log.id}`} className="flex items-start justify-between p-4 border rounded-lg">
                        <div className="flex items-start space-x-4">
                          <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                            <BookOpen className="w-5 h-5 text-orange-600" />
                          </div>
                          <div>
                            <div className="flex items-center space-x-2">
                              <h3 className="font-semibold">{log.title}</h3>
                              <Badge variant={log.isLoftLog ? "default" : "outline"} className="text-xs">
                                {log.isLoftLog ? 'Loft' : 'Individual'}
                              </Badge>
                            </div>
                            {log.isLoftLog ? (
                              <p className="text-sm text-gray-600">Loft: {log.loft_name}</p>
                            ) : (
                              <p className="text-sm text-gray-600">{pigeon?.name || 'Unknown'} - {pigeon?.ring_number}</p>
                            )}
                            <p className="text-sm text-gray-500">{log.date}</p>
                            {log.description && (
                              <p className="text-sm text-gray-600 mt-1">{log.description}</p>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteLog(log)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Sales & Transfers Component
const SalesTransfers = () => {
  const [pigeons, setPigeons] = useState([]);
  const [transfers, setTransfers] = useState([]);
  const [addTransferOpen, setAddTransferOpen] = useState(false);
  const [newTransfer, setNewTransfer] = useState({
    pigeon_id: "",
    recipient_email: "",
    sale_amount: "",
    notes: ""
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchPigeons();
    fetchTransfers();
  }, []);

  const fetchPigeons = async () => {
    try {
      const response = await axios.get(`${API}/pigeons`);
      setPigeons(response.data);
    } catch (error) {
      console.error('Error fetching pigeons:', error);
    }
  };

  const fetchTransfers = async () => {
    try {
      // We'll implement this endpoint later
      setTransfers([]); // For now, empty array
    } catch (error) {
      console.error('Error fetching transfers:', error);
    }
  };

  const handleAddTransfer = async () => {
    if (!newTransfer.pigeon_id || !newTransfer.recipient_email) {
      toast({
        title: "Missing Information",
        description: "Please select a pigeon and enter recipient email",
        variant: "destructive",
      });
      return;
    }

    try {
      // We'll implement this endpoint later
      toast({
        title: "Success!",
        description: "Transfer request sent successfully",
      });
      
      setNewTransfer({
        pigeon_id: "",
        recipient_email: "",
        sale_amount: "",
        notes: ""
      });
      setAddTransferOpen(false);
      fetchTransfers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send transfer request",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sales & Transfers</h1>
          <p className="text-gray-500 mt-1">Manage pigeon sales and transfers to other breeders</p>
        </div>
        
        <Dialog open={addTransferOpen} onOpenChange={setAddTransferOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <ShoppingCart className="w-4 h-4 mr-2" />
              Transfer Pigeon
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Transfer Pigeon</DialogTitle>
              <DialogDescription>Send a pigeon to another breeder</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="pigeon">Select Pigeon *</Label>
                <Select onValueChange={(value) => setNewTransfer({...newTransfer, pigeon_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Pigeon to Transfer" />
                  </SelectTrigger>
                  <SelectContent>
                    {pigeons.map((pigeon) => (
                      <SelectItem key={pigeon.id} value={pigeon.id}>
                        {pigeon.name || 'Unnamed'} - {pigeon.ring_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="recipient_email">Recipient Email *</Label>
                <Input 
                  id="recipient_email"
                  type="email"
                  value={newTransfer.recipient_email}
                  onChange={(e) => setNewTransfer({...newTransfer, recipient_email: e.target.value})}
                  placeholder="buyer@example.com"
                />
              </div>

              <div>
                <Label htmlFor="sale_amount">Sale Amount (Optional)</Label>
                <Input 
                  id="sale_amount"
                  type="number"
                  value={newTransfer.sale_amount}
                  onChange={(e) => setNewTransfer({...newTransfer, sale_amount: e.target.value})}
                  placeholder="0.00"
                />
                <p className="text-xs text-gray-500 mt-1">Amount is private and only visible to you</p>
              </div>

              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea 
                  id="notes"
                  value={newTransfer.notes}
                  onChange={(e) => setNewTransfer({...newTransfer, notes: e.target.value})}
                  placeholder="Any additional notes about this transfer..."
                />
              </div>

              <Button onClick={handleAddTransfer} className="w-full">
                Send Transfer Request
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Total Sales</p>
                <p className="text-2xl font-bold text-green-600">0</p>
                <p className="text-sm text-gray-500">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Transfers</p>
                <p className="text-2xl font-bold text-blue-600">0</p>
                <p className="text-sm text-gray-500">Awaiting acceptance</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Trophy className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Revenue</p>
                <p className="text-2xl font-bold text-yellow-600">€0</p>
                <p className="text-sm text-gray-500">Total earnings</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">This Month</p>
                <p className="text-2xl font-bold text-purple-600">0</p>
                <p className="text-sm text-gray-500">Transfers made</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Transfer Status Tabs */}
      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">All Transfers</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="accepted">Accepted</TabsTrigger>
          <TabsTrigger value="rejected">Rejected</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Transfer History</CardTitle>
              <CardDescription>View all pigeon transfers and their status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <ShoppingCart className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No transfers yet</p>
                <p className="text-sm text-gray-400">Start transferring pigeons to build your transaction history</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pending" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Pending Transfers</CardTitle>
              <CardDescription>Transfers awaiting recipient acceptance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No pending transfers</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="accepted" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Accepted Transfers</CardTitle>
              <CardDescription>Successfully completed transfers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <CheckCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No accepted transfers</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rejected" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Rejected Transfers</CardTitle>
              <CardDescription>Transfers that were declined by recipients</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <X className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No rejected transfers</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Settings Component
const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your account settings and preferences</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="plan">Plan & Billing</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your personal information and breeder details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="first_name">First Name</Label>
                  <Input id="first_name" placeholder="John" />
                </div>
                <div>
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input id="last_name" placeholder="Doe" />
                </div>
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="john@example.com" />
              </div>
              <div>
                <Label htmlFor="breeder_name">Breeder Name</Label>
                <Input id="breeder_name" placeholder="Doe Loft Racing" />
              </div>
              <Button>Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="plan" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Current Plan</CardTitle>
              <CardDescription>Manage your subscription and billing information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-semibold">Free Trial</h3>
                    <p className="text-sm text-gray-500">7 days remaining</p>
                  </div>
                  <Badge variant="secondary">Active</Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Pigeons used:</span>
                    <span>1/5</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Pedigrees created:</span>
                    <span>0/1</span>
                  </div>
                </div>
                <Button className="w-full">Upgrade Plan</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Preferences</CardTitle>
              <CardDescription>Customize your experience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="language">Language</Label>
                <Select defaultValue="en">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="nl">Dutch</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="country">Country</Label>
                <Select defaultValue="be">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="be">Belgium</SelectItem>
                    <SelectItem value="nl">Netherlands</SelectItem>
                    <SelectItem value="de">Germany</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button>Save Preferences</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'my-pigeons':
        return <MyPigeons />;
      case 'race-results':
        return <RaceResults />;
      case 'breeding':
        return <BreedingPairing />;
      case 'health':
        return <HealthTraining />;
      case 'sales':
        return <SalesTransfers />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Main Content */}
      <div className="flex-1 lg:ml-0">
        {/* Mobile Header */}
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => setIsMobileOpen(true)}
            className="text-gray-500 hover:text-gray-700"
          >
            <Menu className="w-6 h-6" />
          </button>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bird className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-lg font-bold text-gray-900">PigeonPedigree</h1>
          </div>
          <div></div>
        </div>

        {/* Page Content */}
        <main className="p-6">
          {renderActiveComponent()}
        </main>
      </div>

      <Toaster />
    </div>
  );
}

export default App;