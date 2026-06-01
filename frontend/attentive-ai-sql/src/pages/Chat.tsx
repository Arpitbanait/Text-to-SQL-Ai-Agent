import { useState, useRef, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Database,
  Send,
  Copy,
  Check,
  ArrowLeft,
  Sparkles,
  History,
  Table2,
  PanelRightOpen,
  PanelRightClose,
  AlertCircle,
} from "lucide-react";
import AnimatedBackground from "@/components/AnimatedBackground";
import TypingAnimation from "@/components/TypingAnimation";
import SchemaViewer from "@/components/SchemaViewer";
import QueryHistory from "@/components/QueryHistory";
import { api, connectionStorage } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sql?: string;
  isTyping?: boolean;
  error?: boolean;
}

const Chat = () => {
  const { connectionId } = useParams();
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showSchema, setShowSchema] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showExplanation, setShowExplanation] = useState(true);
  const [streamReply, setStreamReply] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get connection info
  const connection = connectionId ? connectionStorage.getById(connectionId) : null;

  useEffect(() => {
    if (!connection) {
      toast({
        title: "Connection not found",
        description: "Please select a database connection from the dashboard.",
        variant: "destructive",
      });
    } else if (!connection.indexed) {
      toast({
        title: "Schema not indexed",
        description: "This database hasn't been indexed yet. Some features may be limited.",
      });
    }
  }, [connection, toast]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !connection) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const question = input.trim();
    setInput("");
    setIsLoading(true);

    // Add typing indicator
    const typingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "",
      isTyping: true,
    };
    setMessages((prev) => [...prev, typingMessage]);

    try {
      if (streamReply) {
        const assistantId = (Date.now() + 2).toString();
        // Seed assistant message placeholder
        setMessages((prev) =>
          prev.filter((m) => !m.isTyping).concat({
            id: assistantId,
            role: "assistant",
            content: showExplanation ? "" : "",
          })
        );

        await api.textToSQLStream(
          {
            query: question,
            database_name: connection.database_name,
            include_explanation: showExplanation,
            execute_query: false,
          },
          ({ event, data }) => {
            if (event === "sql") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, sql: data.sql_query } : m
                )
              );
              toast({
                title: "SQL generated",
                description: `Confidence: ${Math.round((data.confidence || 0) * 100)}%`,
              });
            } else if (event === "explanation") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: (m.content || "") + (data.chunk || "") }
                    : m
                )
              );
            } else if (event === "error") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: `Failed to generate SQL: ${data?.detail || "Unknown error"}`,
                        error: true,
                      }
                    : m
                )
              );
            }
          }
        );
      } else {
        // Non-streaming fallback
        const response = await api.textToSQL({
          query: question,
          database_name: connection.database_name,
          include_explanation: showExplanation,
          execute_query: false,
        });

        // Update last used timestamp
        connectionStorage.updateLastUsed(connectionId!);

        // Remove typing indicator and add actual response
        setMessages((prev) =>
          prev
            .filter((m) => !m.isTyping)
            .concat({
              id: (Date.now() + 2).toString(),
              role: "assistant",
              content: showExplanation ? response.explanation || "" : "",
              sql: response.sql,
            })
        );

        toast({
          title: "Query generated successfully",
          description: `Confidence: ${Math.round(response.confidence * 100)}%`,
        });
      }
    } catch (error) {
      // Remove typing indicator and show error
      setMessages((prev) =>
        prev
          .filter((m) => !m.isTyping)
          .concat({
            id: (Date.now() + 2).toString(),
            role: "assistant",
            content: `Failed to generate SQL: ${error instanceof Error ? error.message : 'Unknown error'}`,
            error: true,
          })
      );

      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to generate SQL',
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (sql: string, id: string) => {
    navigator.clipboard.writeText(sql);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleHistorySelect = (query: { question: string; sql: string }) => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        role: "user",
        content: query.question,
      },
      {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Here's the query from your history:",
        sql: query.sql,
      },
    ]);
    setShowHistory(false);
  };

  return (
    <div className="min-h-screen bg-background relative flex">
      <AnimatedBackground />

      {/* Schema Viewer Sidebar */}
      <SchemaViewer 
        isOpen={showSchema} 
        onClose={() => setShowSchema(false)}
        databaseName={connection?.database_name}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* Header */}
        <header className="border-b border-border/50 glass">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                to="/dashboard"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/50 flex items-center justify-center">
                  <Database className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-foreground">
                    {connection?.name || 'Unknown Database'}
                  </h1>
                  <span className="text-xs text-muted-foreground">
                    {connection?.type.toUpperCase()} • {connection?.host}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowSchema(!showSchema)}
                className={`text-muted-foreground hover:text-foreground ${
                  showSchema ? "bg-primary/10 text-primary" : ""
                }`}
              >
                <Table2 className="w-5 h-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowHistory(!showHistory)}
                className={`text-muted-foreground hover:text-foreground ${
                  showHistory ? "bg-primary/10 text-primary" : ""
                }`}
              >
                {showHistory ? (
                  <PanelRightClose className="w-5 h-5" />
                ) : (
                  <PanelRightOpen className="w-5 h-5" />
                )}
              </Button>
              <Button
                variant={showExplanation ? "default" : "outline"}
                size="sm"
                onClick={() => setShowExplanation(!showExplanation)}
                className="ml-2"
              >
                {showExplanation ? "Explanation: On" : "Explanation: Off"}
              </Button>
              <Button
                variant={streamReply ? "default" : "outline"}
                size="sm"
                onClick={() => setStreamReply(!streamReply)}
                className="ml-1"
              >
                {streamReply ? "Stream: On" : "Stream: Off"}
              </Button>
            </div>
          </div>
        </header>
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in">
              <div className="w-16 h-16 rounded-2xl bg-primary/20 border border-primary/50 flex items-center justify-center mb-6 glow-cyan">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-2">
                Ask anything about your data
              </h2>
              <p className="text-muted-foreground max-w-md mb-8">
                Describe what you want to query in plain English, and I'll
                generate the SQL for you.
              </p>
              <div className="flex flex-wrap gap-3 justify-center max-w-xl">
                {[
                  "Show me all users from last week",
                  "Top 10 products by sales",
                  "Average order value by month",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="px-4 py-2 rounded-full glass border-glow-cyan text-sm text-foreground hover:bg-primary/10 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 animate-fade-in ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.role === "assistant" && (
                <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>
              )}

              <div
                className={`max-w-2xl ${
                  message.role === "user" ? "order-first" : ""
                }`}
              >
                {message.isTyping ? (
                  <div className="glass rounded-2xl px-6 py-4 border-glow-cyan">
                    <TypingAnimation />
                  </div>
                ) : (
                  <>
                    <div
                      className={`rounded-2xl px-6 py-4 ${
                        message.role === "user"
                          ? "glass border-glow-purple"
                          : message.error
                          ? "glass border-red-500/50 bg-red-500/10"
                          : "glass border-glow-cyan"
                      }`}
                    >
                      {message.error && (
                        <div className="flex items-center gap-2 mb-2 text-red-400">
                          <AlertCircle className="w-4 h-4" />
                          <span className="text-xs font-semibold">Error</span>
                        </div>
                      )}
                      <p className="text-foreground">{message.content}</p>
                    </div>

                    {message.sql && (
                      <div className="mt-3 relative group">
                        <div className="bg-card/80 border border-primary/30 rounded-xl overflow-hidden animate-pulse-glow">
                          <div className="flex items-center justify-between px-4 py-2 border-b border-border/50 bg-primary/5">
                            <span className="text-xs font-mono text-primary">SQL</span>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="w-8 h-8 text-muted-foreground hover:text-primary"
                              onClick={() => handleCopy(message.sql!, message.id)}
                            >
                              {copiedId === message.id ? (
                                <Check className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4" />
                              )}
                            </Button>
                          </div>
                          <pre className="p-4 overflow-x-auto">
                            <code className="text-sm font-mono text-primary whitespace-pre">
                              {message.sql}
                            </code>
                          </pre>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>

              {message.role === "user" && (
                <div className="w-10 h-10 rounded-full bg-secondary/20 border border-secondary/50 flex items-center justify-center flex-shrink-0 text-sm font-medium text-secondary">
                  JD
                </div>
              )}
            </div>
          ))}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-border/50 p-4 glass">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <Input
                placeholder="Ask a question about your data..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                className="flex-1 bg-input border-border/50 focus:border-primary/50 text-base py-6"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="glow-cyan bg-primary text-primary-foreground hover:bg-primary/90 px-6"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Query History Sidebar */}
      <QueryHistory
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
        onSelect={handleHistorySelect}
      />
    </div>
  );
};

export default Chat;
