import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Database,
  Plus,
  Settings,
  LogOut,
  ChevronRight,
  Server,
  Trash2,
  RefreshCw,
} from "lucide-react";
import AnimatedBackground from "@/components/AnimatedBackground";
import { connectionStorage, formatRelativeTime, type DatabaseConnection } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const dbIcons = {
  postgresql: "🐘",
  mysql: "🐬",
  sqlite: "📁",
  mssql: "🗄️",
};

const dbColors = {
  postgresql: "border-blue-500/50 bg-blue-500/10",
  mysql: "border-orange-500/50 bg-orange-500/10",
  sqlite: "border-green-500/50 bg-green-500/10",
  mssql: "border-purple-500/50 bg-purple-500/10",
};

const Dashboard = () => {
  const { toast } = useToast();
  const [connections, setConnections] = useState<DatabaseConnection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load connections from localStorage on mount
  useEffect(() => {
    const loadConnections = () => {
      try {
        const stored = connectionStorage.getAll();
        setConnections(stored);
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load connections",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadConnections();
  }, [toast]);

  const handleDelete = (id: string) => {
    connectionStorage.delete(id);
    setConnections(connections.filter(c => c.id !== id));
    toast({
      title: "Connection deleted",
      description: "The database connection has been removed.",
    });
  };

  return (
    <div className="min-h-screen bg-background relative">
      <AnimatedBackground />

      {/* Header */}
      <header className="relative z-10 border-b border-border/50 glass">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/50 flex items-center justify-center glow-cyan">
              <Database className="w-5 h-5 text-primary" />
            </div>
            <span className="text-xl font-bold text-foreground">QueryAI</span>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Settings className="w-5 h-5" />
            </Button>
            <div className="w-9 h-9 rounded-full bg-secondary/20 border border-secondary/50 flex items-center justify-center text-sm font-medium text-secondary">
              JD
            </div>
            <Link to="/">
              <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                <LogOut className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        <div className="animate-fade-in">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                My Databases
              </h1>
              <p className="text-muted-foreground">
                Connect and manage your database connections
              </p>
            </div>
            <Link to="/add-connection">
              <Button className="glow-cyan bg-primary text-primary-foreground hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Add Connection
              </Button>
            </Link>
          </div>

          {/* Connections Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {isLoading ? (
              <div className="col-span-full flex items-center justify-center py-12">
                <RefreshCw className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : connections.length === 0 ? (
              <div className="col-span-full text-center py-12">
                <Database className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No connections yet</h3>
                <p className="text-muted-foreground mb-6">
                  Start by adding your first database connection to begin querying.
                </p>
                <Link to="/add-connection">
                  <Button className="glow-cyan bg-primary text-primary-foreground hover:bg-primary/90">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Your First Connection
                  </Button>
                </Link>
              </div>
            ) : (
              <>
                {connections.map((connection, index) => (
                  <Link
                    key={connection.id}
                    to={`/chat/${connection.id}`}
                    className="animate-fade-in-up"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="glass rounded-xl p-6 border-glow-cyan hover:scale-[1.02] transition-all duration-300 group cursor-pointer h-full">
                      <div className="flex items-start justify-between mb-4">
                        <div
                          className={`w-12 h-12 rounded-lg border flex items-center justify-center text-2xl ${
                            dbColors[connection.type]
                          }`}
                        >
                          {dbIcons[connection.type]}
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
                          onClick={(e) => {
                            e.preventDefault();
                            handleDelete(connection.id);
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>

                      <h3 className="text-lg font-semibold text-foreground mb-1">
                        {connection.name}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                        <Server className="w-3 h-3" />
                        {connection.host}
                      </div>

                      {connection.indexed && (
                        <div className="text-xs text-green-400 mb-4">
                          ✓ Schema indexed
                        </div>
                      )}

                      <div className="flex items-center justify-between pt-4 border-t border-border/50">
                        <span className="text-xs text-muted-foreground">
                          Last used: {formatRelativeTime(connection.lastUsed)}
                        </span>
                        <ChevronRight className="w-4 h-4 text-primary group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </Link>
                ))}

                {/* Add new */}
                <Link to="/add-connection">
                  <div className="glass rounded-xl p-6 border-2 border-dashed border-border/50 hover:border-primary/50 transition-colors min-h-[200px] flex flex-col items-center justify-center gap-3 cursor-pointer group">
                    <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center group-hover:glow-cyan transition-all">
                      <Plus className="w-6 h-6 text-primary" />
                    </div>
                    <span className="text-muted-foreground group-hover:text-foreground transition-colors">
                      Add new connection
                    </span>
                  </div>
                </Link>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
