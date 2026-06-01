import { X, Table2, Key, Link as LinkIcon, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface SchemaViewerProps {
  isOpen: boolean;
  onClose: () => void;
  databaseName?: string;
}

interface Column {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
}

interface TableSchema {
  name: string;
  columns: Column[];
}

const SchemaViewer = ({ isOpen, onClose, databaseName }: SchemaViewerProps) => {
  const [schema, setSchema] = useState<TableSchema[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen && databaseName) {
      const fetchSchema = async () => {
        setIsLoading(true);
        setError(null);
        try {
          const data = await api.getSchema(databaseName);
          setSchema(data.tables || []);
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Failed to load schema';
          setError(message);
          toast({
            title: "Error loading schema",
            description: message,
            variant: "destructive",
          });
        } finally {
          setIsLoading(false);
        }
      };

      fetchSchema();
    }
  }, [isOpen, databaseName, toast]);

  if (!isOpen) return null;

  return (
    <div className="w-80 border-r border-border/50 glass overflow-y-auto animate-slide-in-left">
      <div className="sticky top-0 z-10 px-4 py-3 border-b border-border/50 bg-card/80 backdrop-blur flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Table2 className="w-4 h-4 text-primary" />
          <span className="font-medium text-foreground">Schema</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="w-8 h-8 text-muted-foreground hover:text-foreground"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      <div className="p-4 space-y-4">
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-5 h-5 animate-spin text-primary" />
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-400">Error loading schema</p>
              <p className="text-xs text-red-400/80">{error}</p>
            </div>
          </div>
        )}

        {!isLoading && !error && (!schema || schema.length === 0) && (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground">
              {databaseName ? "No tables found in this database" : "Select a database to view schema"}
            </p>
          </div>
        )}

        {schema && schema.map((table, index) => (
          <div
            key={table.name}
            className="glass rounded-lg overflow-hidden border-glow-cyan animate-fade-in"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            {/* Table Header */}
            <div className="px-3 py-2 bg-primary/10 border-b border-border/50">
              <div className="flex items-center gap-2">
                <Table2 className="w-3.5 h-3.5 text-primary" />
                <span className="font-mono text-sm font-medium text-foreground">
                  {table.name}
                </span>
              </div>
            </div>

            {/* Columns */}
            <div className="divide-y divide-border/30">
              {table.columns.map((column) => (
                <div
                  key={column.name}
                  className="px-3 py-2 flex items-center justify-between text-xs hover:bg-muted/30 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    {column.primary_key && (
                      <Key className="w-3 h-3 text-yellow-400" />
                    )}
                    <span
                      className={`font-mono ${
                        column.primary_key ? "text-yellow-400" : "text-foreground"
                      }`}
                    >
                      {column.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <span className="font-mono">{column.type}</span>
                    {column.nullable && (
                      <span className="text-xs text-muted-foreground/60">nullable</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="sticky bottom-0 px-4 py-3 border-t border-border/50 bg-card/80 backdrop-blur">
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Key className="w-3 h-3 text-yellow-400" />
            <span>Primary Key</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground/60">nullable</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchemaViewer;
