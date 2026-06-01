import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ArrowLeft,
  Database,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";
import AnimatedBackground from "@/components/AnimatedBackground";
import { api, connectionStorage, buildConnectionString, type DatabaseConnection } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const AddConnection = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [dbType, setDbType] = useState<'postgresql' | 'mysql' | 'sqlite' | 'mssql' | ''>("");
  const [name, setName] = useState("");
  const [host, setHost] = useState("");
  const [port, setPort] = useState("");
  const [database, setDatabase] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);

  const defaultPorts: Record<string, string> = {
    postgresql: "5432",
    mysql: "3306",
    sqlite: "",
    mssql: "1433",
  };

  const handleDbTypeChange = (value: string) => {
    setDbType(value as typeof dbType);
    setPort(defaultPorts[value] || "");
    setTestResult(null);
  };

  const handleTestConnection = async () => {
    if (!dbType || !name) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      // Build connection string
      const connectionString = buildConnectionString({
        type: dbType as any,
        username,
        password,
        host: host || 'localhost',
        port: port || defaultPorts[dbType],
        database,
      });

      // Test by trying to index (this will validate connection)
      const databaseName = `${name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`;
      
      await api.indexSchema({
        database_name: databaseName,
        connection_string: connectionString,
        database_type: dbType as any,
      });

      setTestResult("success");
      toast({
        title: "Connection successful",
        description: "Your database connection is working correctly.",
      });
    } catch (error) {
      setTestResult("error");
      toast({
        title: "Connection failed",
        description: error instanceof Error ? error.message : 'Please check your credentials and try again.',
        variant: "destructive",
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    if (!dbType || !name) return;

    setIsSaving(true);
    setIsIndexing(true);

    try {
      // Create connection object
      const databaseName = name.toLowerCase().replace(/\s+/g, '_');
      const connectionString = buildConnectionString({
        type: dbType as any,
        username,
        password,
        host: host || 'localhost',
        port: port || defaultPorts[dbType],
        database,
      });

      const connection: DatabaseConnection = {
        id: Date.now().toString(),
        name,
        database_name: databaseName,
        type: dbType as any,
        host: host || 'localhost',
        port: port || defaultPorts[dbType],
        database,
        username,
        password, // Note: In production, don't store passwords in localStorage
        connection_string: connectionString,
        lastUsed: new Date().toISOString(),
        indexed: false,
      };

      // Save to localStorage
      connectionStorage.save(connection);

      // Index schema in background
      toast({
        title: "Indexing schema...",
        description: "This may take a moment. You'll be notified when it's done.",
      });

      try {
        await api.indexSchema({
          database_name: databaseName,
          connection_string: connectionString,
          database_type: dbType as any,
        });

        // Mark as indexed
        connectionStorage.markIndexed(connection.id);

        toast({
          title: "Success!",
          description: "Database connected and schema indexed successfully.",
        });
      } catch (error) {
        toast({
          title: "Connection saved",
          description: "But schema indexing failed. You can retry from the dashboard.",
        });
      }

      navigate("/dashboard");
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to save connection',
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
      setIsIndexing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden py-12">
      <AnimatedBackground />

      <div className="relative z-10 max-w-2xl mx-auto px-6 animate-fade-in-up">
        {/* Back button */}
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to dashboard
        </Link>

        {/* Form Card */}
        <div className="glass rounded-2xl p-8 border-glow-cyan">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary/20 border border-primary/50 flex items-center justify-center glow-cyan">
              <Database className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Add Database Connection
              </h1>
              <p className="text-muted-foreground">
                Connect your database to start querying
              </p>
            </div>
          </div>

          <form className="space-y-6">
            {/* Connection Name */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-foreground">
                Connection Name
              </Label>
              <Input
                id="name"
                placeholder="My Production Database"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="bg-input border-border/50 focus:border-primary/50"
              />
            </div>

            {/* Database Type */}
            <div className="space-y-2">
              <Label htmlFor="dbType" className="text-foreground">
                Database Type
              </Label>
              <Select value={dbType} onValueChange={handleDbTypeChange}>
                <SelectTrigger className="bg-input border-border/50 focus:border-primary/50">
                  <SelectValue placeholder="Select database type" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="postgresql">
                    <span className="flex items-center gap-2">
                      🐘 PostgreSQL
                    </span>
                  </SelectItem>
                  <SelectItem value="mysql">
                    <span className="flex items-center gap-2">🐬 MySQL</span>
                  </SelectItem>
                  <SelectItem value="sqlite">
                    <span className="flex items-center gap-2">📁 SQLite</span>
                  </SelectItem>
                  <SelectItem value="mssql">
                    <span className="flex items-center gap-2">🗄️ SQL Server</span>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {dbType && dbType !== "sqlite" && (
              <>
                {/* Host & Port */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-2 space-y-2">
                    <Label htmlFor="host" className="text-foreground">
                      Host
                    </Label>
                    <Input
                      id="host"
                      placeholder="localhost or db.example.com"
                      value={host}
                      onChange={(e) => setHost(e.target.value)}
                      className="bg-input border-border/50 focus:border-primary/50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="port" className="text-foreground">
                      Port
                    </Label>
                    <Input
                      id="port"
                      placeholder={defaultPorts[dbType]}
                      value={port}
                      onChange={(e) => setPort(e.target.value)}
                      className="bg-input border-border/50 focus:border-primary/50"
                    />
                  </div>
                </div>

                {/* Database Name */}
                <div className="space-y-2">
                  <Label htmlFor="database" className="text-foreground">
                    Database Name
                  </Label>
                  <Input
                    id="database"
                    placeholder="myapp_production"
                    value={database}
                    onChange={(e) => setDatabase(e.target.value)}
                    className="bg-input border-border/50 focus:border-primary/50"
                  />
                </div>

                {/* Username */}
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-foreground">
                    Username
                  </Label>
                  <Input
                    id="username"
                    placeholder="postgres"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="bg-input border-border/50 focus:border-primary/50"
                  />
                </div>

                {/* Password */}
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-foreground">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-input border-border/50 focus:border-primary/50"
                  />
                </div>
              </>
            )}

            {dbType === "sqlite" && (
              <div className="space-y-2">
                <Label htmlFor="filepath" className="text-foreground">
                  Database File Path
                </Label>
                <Input
                  id="filepath"
                  placeholder="/path/to/database.sqlite"
                  value={database}
                  onChange={(e) => setDatabase(e.target.value)}
                  className="bg-input border-border/50 focus:border-primary/50"
                />
              </div>
            )}

            {/* Test Connection Result */}
            {testResult && (
              <div
                className={`flex items-center gap-3 p-4 rounded-lg animate-scale-in ${
                  testResult === "success"
                    ? "bg-green-500/10 border border-green-500/30"
                    : "bg-destructive/10 border border-destructive/30"
                }`}
              >
                {testResult === "success" ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-green-400">
                      Connection successful! Your database is ready.
                    </span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-destructive" />
                    <span className="text-destructive">
                      Connection failed. Please check your credentials.
                    </span>
                  </>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={handleTestConnection}
                disabled={!dbType || isTesting}
                className="flex-1 border-border/50 hover:border-primary/50 hover:bg-primary/10"
              >
                {isTesting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  "Test Connection"
                )}
              </Button>
              <Button
                type="button"
                onClick={handleSave}
                disabled={!dbType || !name || isSaving || isIndexing}
                className="flex-1 glow-cyan bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {isSaving || isIndexing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {isIndexing ? "Indexing..." : "Saving..."}
                  </>
                ) : (
                  "Save & Index"
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddConnection;
