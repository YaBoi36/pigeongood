import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
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
  X
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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sidebar Navigation Component
const Sidebar = ({ activeTab, setActiveTab, isMobileOpen, setIsMobileOpen }) => {
  const menuItems = [
    { key: 'dashboard', label: 'Dashboard', icon: Home },
    { key: 'my-pigeons', label: 'My Pigeons', icon: Bird },
    { key: 'race-results', label: 'Race Results', icon: Trophy },
    { key: 'breeding', label: 'Breeding & Pairing', icon: Heart },
    { key: 'health', label: 'Health & Training', icon: Medal },
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
              <p className="text-sm text-gray-500">Racing Performance</p>
            </div>
          </div>
          
          <div className="flex space-x-6">
            <Link 
              to="/race-results" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                location.pathname === '/race-results' 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Trophy className="w-4 h-4" />
              <span>Race Results</span>
            </Link>
            <Link 
              to="/my-pigeons" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                location.pathname === '/my-pigeons' 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Bird className="w-4 h-4" />
              <span>My Pigeons</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Race Results Page Component
const RaceResults = () => {
  const [dashboardStats, setDashboardStats] = useState({});
  const [raceResults, setRaceResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [resultToDelete, setResultToDelete] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [parsedPigeonCounts, setParsedPigeonCounts] = useState([]);
  const [confirmedPigeonCount, setConfirmedPigeonCount] = useState('');
  const { toast } = useToast();

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
      setLoading(false);
    } catch (error) {
      console.error('Error fetching race results:', error);
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setSelectedFile(file);
  };

  const handleInitialUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    
    setUploading(true);
    try {
      const response = await axios.post(`${API}/upload-race-results`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data.needs_pigeon_count_confirmation) {
        setParsedPigeonCounts(response.data.parsed_pigeon_counts);
        setConfirmedPigeonCount(response.data.parsed_pigeon_counts[0]?.toString() || '');
        setUploadDialogOpen(false);
        setConfirmDialogOpen(true);
      } else {
        toast({
          title: "Success!",
          description: response.data.message,
        });
        setUploadDialogOpen(false);
        fetchDashboardStats();
        fetchRaceResults();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to upload file",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmedUpload = async () => {
    if (!selectedFile || !confirmedPigeonCount) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('confirmed_pigeon_count', confirmedPigeonCount);
    
    setUploading(true);
    try {
      const response = await axios.post(`${API}/confirm-race-upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast({
        title: "Success!",
        description: response.data.message,
      });
      
      setConfirmDialogOpen(false);
      setSelectedFile(null);
      setConfirmedPigeonCount('');
      fetchDashboardStats();
      fetchRaceResults();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to upload file",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteRaceResult = async (resultId) => {
    setResultToDelete(resultId);
    setDeleteConfirmOpen(true);
  };

  const confirmDeleteRaceResult = async () => {
    if (!resultToDelete) return;
    
    try {
      await axios.delete(`${API}/race-results/${resultToDelete}`);
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
        variant: "destructive"
      });
    } finally {
      setDeleteConfirmOpen(false);
      setResultToDelete(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Race Results</h1>
          <p className="text-gray-500 mt-1">Track and analyze your pigeons' racing performance with detailed statistics and insights.</p>
        </div>
        
        <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
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
                Upload a TXT file containing race results to automatically populate pigeon performance data.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="file-upload">Select TXT File</Label>
                <Input 
                  id="file-upload"
                  type="file" 
                  accept=".txt"
                  onChange={handleFileSelect}
                  disabled={uploading}
                />
              </div>
              {selectedFile && (
                <div className="flex items-center space-x-2 text-green-600">
                  <span>File selected: {selectedFile.name}</span>
                </div>
              )}
              {uploading && (
                <div className="flex items-center space-x-2 text-blue-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span>Processing file...</span>
                </div>
              )}
              <Button 
                onClick={handleInitialUpload} 
                disabled={!selectedFile || uploading}
                className="w-full"
              >
                Upload and Parse File
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Pigeon Count Confirmation Dialog */}
        <Dialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Confirm Pigeon Count</DialogTitle>
              <DialogDescription>
                We detected {parsedPigeonCounts.length > 0 ? parsedPigeonCounts[0] : 'unknown'} pigeons from the file. 
                Please confirm the exact number of pigeons that participated in this race for accurate coefficient calculation.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="pigeon-count">Number of Pigeons in Race</Label>
                <Input 
                  id="pigeon-count"
                  type="number"
                  value={confirmedPigeonCount}
                  onChange={(e) => setConfirmedPigeonCount(e.target.value)}
                  placeholder="Enter exact number"
                  min="1"
                  max="5000"
                />
                <p className="text-sm text-gray-500 mt-1">
                  This will be used to calculate coefficients: (position × 100) ÷ total pigeons
                </p>
              </div>
              {uploading && (
                <div className="flex items-center space-x-2 text-blue-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span>Processing race results...</span>
                </div>
              )}
              <div className="flex space-x-2">
                <Button 
                  onClick={handleConfirmedUpload} 
                  disabled={!confirmedPigeonCount || uploading}
                  className="flex-1"
                >
                  Confirm and Process
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setConfirmDialogOpen(false)}
                  disabled={uploading}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Top Performers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {dashboardStats.top_performers?.map((performer, index) => (
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
                  <span className="text-sm text-gray-600">Total Wins</span>
                  <span className="font-semibold">{performer.total_races}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Win Rate</span>
                  <span className="font-semibold">75%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Avg Placement</span>
                  <span className="font-semibold">{performer.best_position}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Best Speed</span>
                  <span className="font-semibold">{performer.avg_speed} m/min</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filter Results */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filter Results</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <Select>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Pigeons" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Pigeons</SelectItem>
              </SelectContent>
            </Select>
            
            <Select>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="young">Young Birds</SelectItem>
                <SelectItem value="old">Old Birds</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline">
              <Search className="w-4 h-4 mr-2" />
              Export Results
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Performance Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
                <p className="text-sm font-medium text-gray-600">Total Wins</p>
                <p className="text-3xl font-bold text-green-600">{dashboardStats.total_wins || 0}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Medal className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Win rate: {dashboardStats.total_results > 0 ? Math.round((dashboardStats.total_wins / dashboardStats.total_results * 100)) : 0}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Win Rate</p>
                <p className="text-3xl font-bold text-purple-600">
                  {dashboardStats.total_results > 0 ? Math.round((dashboardStats.total_wins / dashboardStats.total_results * 100)) : 0}%
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Performance rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Best Speed</p>
                <p className="text-3xl font-bold text-orange-600">
                  {dashboardStats.top_performers?.[0]?.avg_speed || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Timer className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">m/min</p>
          </CardContent>
        </Card>
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
                    <p className="font-semibold">{result.race?.participants || 0}</p>
                    <p className="text-gray-500">Participants</p>
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

// My Pigeons Page Component  
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
        title: "Error",
        description: "Please select a country",
        variant: "destructive"
      });
      return;
    }
    
    if (!newPigeon.ring_number || !/^\d+$/.test(newPigeon.ring_number)) {
      toast({
        title: "Error", 
        description: "Ring number must contain only numbers",
        variant: "destructive"
      });
      return;
    }

    try {
      // Format ring number as COUNTRY + NUMBER
      const formattedPigeon = {
        ...newPigeon,
        ring_number: newPigeon.country + newPigeon.ring_number
      };
      
      const response = await axios.post(`${API}/pigeons`, formattedPigeon);
      setPigeons([...pigeons, response.data]);
      setAddPigeonOpen(false);
      setNewPigeon({
        ring_number: "",
        name: "",
        country: "",
        gender: "",
        color: "",
        breeder: "",
        sire_ring: "",
        dam_ring: ""
      });
      toast({
        title: "Success!",
        description: "Pigeon added successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add pigeon",
        variant: "destructive"
      });
    }
  };

  const handleEditPigeon = async () => {
    try {
      const response = await axios.put(`${API}/pigeons/${currentPigeon.id}`, currentPigeon);
      setPigeons(pigeons.map(p => p.id === currentPigeon.id ? response.data : p));
      setEditPigeonOpen(false);
      setCurrentPigeon(null);
      toast({
        title: "Success!",
        description: "Pigeon updated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to update pigeon",
        variant: "destructive"
      });
    }
  };

  const handleDeletePigeon = async (pigeonId) => {
    if (!window.confirm("Are you sure you want to delete this pigeon?")) return;
    
    try {
      await axios.delete(`${API}/pigeons/${pigeonId}`);
      setPigeons(pigeons.filter(p => p.id !== pigeonId));
      toast({
        title: "Success!",
        description: "Pigeon deleted successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete pigeon",
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
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
                      <SelectItem value="US">United States (US)</SelectItem>
                      <SelectItem value="CA">Canada (CA)</SelectItem>
                      <SelectItem value="AU">Australia (AU)</SelectItem>
                      <SelectItem value="ZA">South Africa (ZA)</SelectItem>
                      <SelectItem value="CN">China (CN)</SelectItem>
                      <SelectItem value="JP">Japan (JP)</SelectItem>
                      <SelectItem value="TW">Taiwan (TW)</SelectItem>
                      <SelectItem value="TH">Thailand (TH)</SelectItem>
                      <SelectItem value="PH">Philippines (PH)</SelectItem>
                      <SelectItem value="MY">Malaysia (MY)</SelectItem>
                      <SelectItem value="SG">Singapore (SG)</SelectItem>
                      <SelectItem value="IN">India (IN)</SelectItem>
                      <SelectItem value="PK">Pakistan (PK)</SelectItem>
                      <SelectItem value="BD">Bangladesh (BD)</SelectItem>
                      <SelectItem value="LK">Sri Lanka (LK)</SelectItem>
                      <SelectItem value="AE">UAE (AE)</SelectItem>
                      <SelectItem value="SA">Saudi Arabia (SA)</SelectItem>
                      <SelectItem value="EG">Egypt (EG)</SelectItem>
                      <SelectItem value="MA">Morocco (MA)</SelectItem>
                      <SelectItem value="TN">Tunisia (TN)</SelectItem>
                      <SelectItem value="DZ">Algeria (DZ)</SelectItem>
                      <SelectItem value="ES">Spain (ES)</SelectItem>
                      <SelectItem value="PT">Portugal (PT)</SelectItem>
                      <SelectItem value="IT">Italy (IT)</SelectItem>
                      <SelectItem value="CH">Switzerland (CH)</SelectItem>
                      <SelectItem value="AT">Austria (AT)</SelectItem>
                      <SelectItem value="PL">Poland (PL)</SelectItem>
                      <SelectItem value="CZ">Czech Republic (CZ)</SelectItem>
                      <SelectItem value="SK">Slovakia (SK)</SelectItem>
                      <SelectItem value="HU">Hungary (HU)</SelectItem>
                      <SelectItem value="RO">Romania (RO)</SelectItem>
                      <SelectItem value="BG">Bulgaria (BG)</SelectItem>
                      <SelectItem value="GR">Greece (GR)</SelectItem>
                      <SelectItem value="TR">Turkey (TR)</SelectItem>
                      <SelectItem value="RU">Russia (RU)</SelectItem>
                      <SelectItem value="UA">Ukraine (UA)</SelectItem>
                      <SelectItem value="BY">Belarus (BY)</SelectItem>
                      <SelectItem value="LT">Lithuania (LT)</SelectItem>
                      <SelectItem value="LV">Latvia (LV)</SelectItem>
                      <SelectItem value="EE">Estonia (EE)</SelectItem>
                      <SelectItem value="FI">Finland (FI)</SelectItem>
                      <SelectItem value="SE">Sweden (SE)</SelectItem>
                      <SelectItem value="NO">Norway (NO)</SelectItem>
                      <SelectItem value="DK">Denmark (DK)</SelectItem>
                      <SelectItem value="IS">Iceland (IS)</SelectItem>
                      <SelectItem value="IE">Ireland (IE)</SelectItem>
                      <SelectItem value="MX">Mexico (MX)</SelectItem>
                      <SelectItem value="AR">Argentina (AR)</SelectItem>
                      <SelectItem value="BR">Brazil (BR)</SelectItem>
                      <SelectItem value="CL">Chile (CL)</SelectItem>
                      <SelectItem value="CO">Colombia (CO)</SelectItem>
                      <SelectItem value="PE">Peru (PE)</SelectItem>
                      <SelectItem value="VE">Venezuela (VE)</SelectItem>
                      <SelectItem value="EC">Ecuador (EC)</SelectItem>
                      <SelectItem value="UY">Uruguay (UY)</SelectItem>
                      <SelectItem value="PY">Paraguay (PY)</SelectItem>
                      <SelectItem value="BO">Bolivia (BO)</SelectItem>
                      <SelectItem value="CR">Costa Rica (CR)</SelectItem>
                      <SelectItem value="PA">Panama (PA)</SelectItem>
                      <SelectItem value="GT">Guatemala (GT)</SelectItem>
                      <SelectItem value="HN">Honduras (HN)</SelectItem>
                      <SelectItem value="SV">El Salvador (SV)</SelectItem>
                      <SelectItem value="NI">Nicaragua (NI)</SelectItem>
                      <SelectItem value="BZ">Belize (BZ)</SelectItem>
                      <SelectItem value="JM">Jamaica (JM)</SelectItem>
                      <SelectItem value="CU">Cuba (CU)</SelectItem>
                      <SelectItem value="DO">Dominican Republic (DO)</SelectItem>
                      <SelectItem value="HT">Haiti (HT)</SelectItem>
                      <SelectItem value="TT">Trinidad and Tobago (TT)</SelectItem>
                      <SelectItem value="BB">Barbados (BB)</SelectItem>
                      <SelectItem value="GY">Guyana (GY)</SelectItem>
                      <SelectItem value="SR">Suriname (SR)</SelectItem>
                      <SelectItem value="GF">French Guiana (GF)</SelectItem>
                      <SelectItem value="FK">Falkland Islands (FK)</SelectItem>
                      <SelectItem value="OTHER">Other</SelectItem>
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
              <Button 
                onClick={handleAddPigeon} 
                className="w-full"
                disabled={!newPigeon.country || !newPigeon.ring_number || !newPigeon.name || !newPigeon.gender}
              >
                Add Pigeon
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search and Filter */}
      <div className="flex space-x-4 mb-6">
        <div className="relative flex-1">
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
            <SelectItem value="Male">Male</SelectItem>
            <SelectItem value="Female">Female</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          Advanced Filters
        </Button>
      </div>

      {/* Plan Usage Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Plan Usage</p>
                <p className="text-2xl font-bold text-blue-600">{pigeons.length}/100</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">{100 - pigeons.length} slots remaining</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Birds</p>
                <p className="text-2xl font-bold text-green-600">{pigeons.length}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Bird className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Currently in loft</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recent Additions</p>
                <p className="text-2xl font-bold text-purple-600">2</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Plus className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">This month</p>
          </CardContent>
        </Card>
      </div>

      {/* Pigeon Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pigeons.map((pigeon) => (
          <Card key={pigeon.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Bird className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{pigeon.name}</CardTitle>
                    <CardDescription>{pigeon.ring_number}</CardDescription>
                  </div>
                </div>
                <Badge variant={pigeon.gender === 'Male' ? 'default' : 'secondary'}>
                  {pigeon.gender}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
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
                    <p className="font-semibold">{pigeon.color}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Breeder</span>
                    <p className="font-semibold">{pigeon.breeder}</p>
                  </div>
                </div>
                
                {(pigeon.sire_ring || pigeon.dam_ring) && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Parent Information</p>
                    <div className="space-y-1 text-sm">
                      {pigeon.sire_ring && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Sire</span>
                          <span>{pigeon.sire_ring}</span>
                        </div>
                      )}
                      {pigeon.dam_ring && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Dam</span>
                          <span>{pigeon.dam_ring}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="flex space-x-2 pt-4">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="w-4 h-4 mr-1" />
                    View Profile
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      setCurrentPigeon(pigeon);
                      setEditPigeonOpen(true);
                    }}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeletePigeon(pigeon.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Edit Pigeon Dialog */}
      <Dialog open={editPigeonOpen} onOpenChange={setEditPigeonOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Pigeon</DialogTitle>
            <DialogDescription>Update pigeon information</DialogDescription>
          </DialogHeader>
          {currentPigeon && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit_ring_number">Ring Number</Label>
                <Input 
                  id="edit_ring_number"
                  value={currentPigeon.ring_number}
                  onChange={(e) => setCurrentPigeon({...currentPigeon, ring_number: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="edit_name">Name</Label>
                <Input 
                  id="edit_name"
                  value={currentPigeon.name}
                  onChange={(e) => setCurrentPigeon({...currentPigeon, name: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit_country">Country</Label>
                  <Select 
                    value={currentPigeon.country}
                    onValueChange={(value) => setCurrentPigeon({...currentPigeon, country: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="BE">Belgium (BE)</SelectItem>
                      <SelectItem value="NL">Netherlands (NL)</SelectItem>
                      <SelectItem value="DE">Germany (DE)</SelectItem>
                      <SelectItem value="FR">France (FR)</SelectItem>
                      <SelectItem value="GB">United Kingdom (GB)</SelectItem>
                      <SelectItem value="DV">DV (Special)</SelectItem>
                      <SelectItem value="US">United States (US)</SelectItem>
                      <SelectItem value="CA">Canada (CA)</SelectItem>
                      <SelectItem value="AU">Australia (AU)</SelectItem>
                      <SelectItem value="ZA">South Africa (ZA)</SelectItem>
                      <SelectItem value="CN">China (CN)</SelectItem>
                      <SelectItem value="JP">Japan (JP)</SelectItem>
                      <SelectItem value="TW">Taiwan (TW)</SelectItem>
                      <SelectItem value="TH">Thailand (TH)</SelectItem>
                      <SelectItem value="PH">Philippines (PH)</SelectItem>
                      <SelectItem value="MY">Malaysia (MY)</SelectItem>
                      <SelectItem value="SG">Singapore (SG)</SelectItem>
                      <SelectItem value="IN">India (IN)</SelectItem>
                      <SelectItem value="PK">Pakistan (PK)</SelectItem>
                      <SelectItem value="BD">Bangladesh (BD)</SelectItem>
                      <SelectItem value="LK">Sri Lanka (LK)</SelectItem>
                      <SelectItem value="AE">UAE (AE)</SelectItem>
                      <SelectItem value="SA">Saudi Arabia (SA)</SelectItem>
                      <SelectItem value="EG">Egypt (EG)</SelectItem>
                      <SelectItem value="MA">Morocco (MA)</SelectItem>
                      <SelectItem value="TN">Tunisia (TN)</SelectItem>
                      <SelectItem value="DZ">Algeria (DZ)</SelectItem>
                      <SelectItem value="ES">Spain (ES)</SelectItem>
                      <SelectItem value="PT">Portugal (PT)</SelectItem>
                      <SelectItem value="IT">Italy (IT)</SelectItem>
                      <SelectItem value="CH">Switzerland (CH)</SelectItem>
                      <SelectItem value="AT">Austria (AT)</SelectItem>
                      <SelectItem value="PL">Poland (PL)</SelectItem>
                      <SelectItem value="CZ">Czech Republic (CZ)</SelectItem>
                      <SelectItem value="SK">Slovakia (SK)</SelectItem>
                      <SelectItem value="HU">Hungary (HU)</SelectItem>
                      <SelectItem value="RO">Romania (RO)</SelectItem>
                      <SelectItem value="BG">Bulgaria (BG)</SelectItem>
                      <SelectItem value="GR">Greece (GR)</SelectItem>
                      <SelectItem value="TR">Turkey (TR)</SelectItem>
                      <SelectItem value="RU">Russia (RU)</SelectItem>
                      <SelectItem value="UA">Ukraine (UA)</SelectItem>
                      <SelectItem value="BY">Belarus (BY)</SelectItem>
                      <SelectItem value="LT">Lithuania (LT)</SelectItem>
                      <SelectItem value="LV">Latvia (LV)</SelectItem>
                      <SelectItem value="EE">Estonia (EE)</SelectItem>
                      <SelectItem value="FI">Finland (FI)</SelectItem>
                      <SelectItem value="SE">Sweden (SE)</SelectItem>
                      <SelectItem value="NO">Norway (NO)</SelectItem>
                      <SelectItem value="DK">Denmark (DK)</SelectItem>
                      <SelectItem value="IS">Iceland (IS)</SelectItem>
                      <SelectItem value="IE">Ireland (IE)</SelectItem>
                      <SelectItem value="MX">Mexico (MX)</SelectItem>
                      <SelectItem value="AR">Argentina (AR)</SelectItem>
                      <SelectItem value="BR">Brazil (BR)</SelectItem>
                      <SelectItem value="CL">Chile (CL)</SelectItem>
                      <SelectItem value="CO">Colombia (CO)</SelectItem>
                      <SelectItem value="PE">Peru (PE)</SelectItem>
                      <SelectItem value="VE">Venezuela (VE)</SelectItem>
                      <SelectItem value="EC">Ecuador (EC)</SelectItem>
                      <SelectItem value="UY">Uruguay (UY)</SelectItem>
                      <SelectItem value="PY">Paraguay (PY)</SelectItem>
                      <SelectItem value="BO">Bolivia (BO)</SelectItem>
                      <SelectItem value="CR">Costa Rica (CR)</SelectItem>
                      <SelectItem value="PA">Panama (PA)</SelectItem>
                      <SelectItem value="GT">Guatemala (GT)</SelectItem>
                      <SelectItem value="HN">Honduras (HN)</SelectItem>
                      <SelectItem value="SV">El Salvador (SV)</SelectItem>
                      <SelectItem value="NI">Nicaragua (NI)</SelectItem>
                      <SelectItem value="BZ">Belize (BZ)</SelectItem>
                      <SelectItem value="JM">Jamaica (JM)</SelectItem>
                      <SelectItem value="CU">Cuba (CU)</SelectItem>
                      <SelectItem value="DO">Dominican Republic (DO)</SelectItem>
                      <SelectItem value="HT">Haiti (HT)</SelectItem>
                      <SelectItem value="TT">Trinidad and Tobago (TT)</SelectItem>
                      <SelectItem value="BB">Barbados (BB)</SelectItem>
                      <SelectItem value="GY">Guyana (GY)</SelectItem>
                      <SelectItem value="SR">Suriname (SR)</SelectItem>
                      <SelectItem value="GF">French Guiana (GF)</SelectItem>
                      <SelectItem value="FK">Falkland Islands (FK)</SelectItem>
                      <SelectItem value="OTHER">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit_gender">Gender</Label>
                  <Select 
                    value={currentPigeon.gender}
                    onValueChange={(value) => setCurrentPigeon({...currentPigeon, gender: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
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
                  <Label htmlFor="edit_color">Color</Label>
                  <Input 
                    id="edit_color"
                    value={currentPigeon.color}
                    onChange={(e) => setCurrentPigeon({...currentPigeon, color: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="edit_breeder">Breeder</Label>
                  <Input 
                    id="edit_breeder"
                    value={currentPigeon.breeder}
                    onChange={(e) => setCurrentPigeon({...currentPigeon, breeder: e.target.value})}
                  />
                </div>
              </div>
              <Button onClick={handleEditPigeon} className="w-full">Update Pigeon</Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<RaceResults />} />
          <Route path="/race-results" element={<RaceResults />} />
          <Route path="/my-pigeons" element={<MyPigeons />} />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </div>
  );
}

export default App;