import { X, History, Trash2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

interface QueryHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (query: { question: string; sql: string }) => void;
}

const mockHistory = [
  {
    id: "1",
    question: "Show me all users who signed up this month",
    sql: "SELECT * FROM users WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);",
    timestamp: "2 hours ago",
  },
  {
    id: "2",
    question: "Top 10 products by revenue",
    sql: "SELECT p.name, SUM(o.quantity * o.price) as revenue FROM products p JOIN orders o ON p.id = o.product_id GROUP BY p.id ORDER BY revenue DESC LIMIT 10;",
    timestamp: "5 hours ago",
  },
  {
    id: "3",
    question: "Users with most orders",
    sql: "SELECT u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id ORDER BY order_count DESC;",
    timestamp: "1 day ago",
  },
  {
    id: "4",
    question: "Average order value by month",
    sql: "SELECT DATE_TRUNC('month', created_at) as month, AVG(total) as avg_value FROM orders GROUP BY month ORDER BY month DESC;",
    timestamp: "2 days ago",
  },
  {
    id: "5",
    question: "Products low on stock",
    sql: "SELECT name, stock FROM products WHERE stock < 10 ORDER BY stock ASC;",
    timestamp: "3 days ago",
  },
];

const QueryHistory = ({ isOpen, onClose, onSelect }: QueryHistoryProps) => {
  const [search, setSearch] = useState("");
  const [history, setHistory] = useState(mockHistory);

  const filteredHistory = history.filter((item) =>
    item.question.toLowerCase().includes(search.toLowerCase())
  );

  const handleDelete = (id: string) => {
    setHistory((prev) => prev.filter((item) => item.id !== id));
  };

  if (!isOpen) return null;

  return (
    <div className="w-80 border-l border-border/50 glass overflow-hidden flex flex-col animate-slide-in-right">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border/50 bg-card/80 backdrop-blur">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-primary" />
            <span className="font-medium text-foreground">Query History</span>
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

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search queries..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-input border-border/50 focus:border-primary/50 text-sm"
          />
        </div>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {filteredHistory.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No queries found
          </div>
        ) : (
          filteredHistory.map((item, index) => (
            <div
              key={item.id}
              className="glass rounded-lg p-3 group cursor-pointer hover:border-primary/30 transition-all animate-fade-in"
              style={{ animationDelay: `${index * 0.05}s` }}
              onClick={() => onSelect({ question: item.question, sql: item.sql })}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <p className="text-sm text-foreground line-clamp-2 flex-1">
                  {item.question}
                </p>
                <Button
                  variant="ghost"
                  size="icon"
                  className="w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive flex-shrink-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(item.id);
                  }}
                >
                  <Trash2 className="w-3 h-3" />
                </Button>
              </div>
              <pre className="text-xs font-mono text-primary/70 line-clamp-2 mb-2 bg-primary/5 rounded p-2 overflow-hidden">
                {item.sql}
              </pre>
              <span className="text-xs text-muted-foreground">
                {item.timestamp}
              </span>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      {history.length > 0 && (
        <div className="px-4 py-3 border-t border-border/50 bg-card/80 backdrop-blur">
          <Button
            variant="ghost"
            size="sm"
            className="w-full text-muted-foreground hover:text-destructive"
            onClick={() => setHistory([])}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear All History
          </Button>
        </div>
      )}
    </div>
  );
};

export default QueryHistory;
