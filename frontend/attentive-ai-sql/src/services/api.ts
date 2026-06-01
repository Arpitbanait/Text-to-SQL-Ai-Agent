// API Service Layer for Backend Integration

const RAW_API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

const API_BASE_URL = RAW_API_BASE_URL.replace(/\/$/, "");

function getFriendlyNetworkError(error: unknown): Error {
  if (error instanceof Error) {
    if (error.name === "TypeError") {
      return new Error(
        `Cannot reach backend at ${API_BASE_URL}. Ensure backend is running and CORS is enabled.`
      );
    }
    return error;
  }

  return new Error("Unexpected network error");
}

async function readErrorMessage(response: Response, fallback: string): Promise<string> {
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('text/event-stream')) {
    const raw = await response.text();
    const sseDetail = extractSseErrorDetail(raw);
    return sseDetail || `${fallback} (HTTP ${response.status})`;
  }

  try {
    const data = await response.json();
    return data?.detail || data?.message || fallback;
  } catch {
    try {
      const raw = await response.text();
      return raw?.trim() || `${fallback} (HTTP ${response.status})`;
    } catch {
      return `${fallback} (HTTP ${response.status})`;
    }
  }
}

function extractSseErrorDetail(raw: string): string {
  if (!raw) return '';

  let detail = '';
  const messages = raw.split('\n\n');

  for (const msg of messages) {
    const lines = msg.split('\n');
    let event = '';
    let data = '';

    for (const line of lines) {
      if (line.startsWith('event:')) event = line.replace('event:', '').trim();
      if (line.startsWith('data:')) data += line.replace('data:', '').trim();
    }

    if (event === 'error' && data) {
      try {
        const parsed = JSON.parse(data);
        detail = parsed?.detail || data;
      } catch {
        detail = data;
      }
      break;
    }
  }

  return detail;
}
// Types matching backend schemas
export interface TextToSQLRequest {
  query: string;
  database_name: string;
  include_explanation?: boolean;
  execute_query?: boolean;
}

export interface TextToSQLResponse {
  sql: string;
  explanation?: string;
  confidence: number;
  database_name: string;
  tables_used?: string[];
  execution_result?: any;
}

export interface SchemaIndexRequest {
  database_name: string;
  connection_string: string;
  database_type: 'postgresql' | 'mysql' | 'sqlite' | 'mssql';
}

export interface SchemaIndexResponse {
  success: boolean;
  message: string;
  database_name: string;
  tables_indexed: number;
}

export interface DatabaseSchema {
  database_name: string;
  tables: Array<{
    name: string;
    columns: Array<{
      name: string;
      type: string;
      nullable: boolean;
      primary_key: boolean;
    }>;
  }>;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  database_connection: boolean;
  vector_store_status: string;
}

// API Functions
export const api = {
  // Health Check
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`);
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, "Health check failed"));
      }
      return response.json();
    } catch (error) {
      throw getFriendlyNetworkError(error);
    }
  },

  // Text to SQL Conversion
  async textToSQL(request: TextToSQLRequest): Promise<TextToSQLResponse> {
    const payload = {
      query: request.query,
      database_name: request.database_name,
      include_explanation: request.include_explanation ?? true,
      execute_query: request.execute_query ?? false,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/query/text-to-sql`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to generate SQL'));
      }

      const data = await response.json();
      // Map backend response (sql_query, explanation, confidence, tables_used, execution_result)
      const mapped: TextToSQLResponse = {
        sql: data.sql_query,
        explanation: data.explanation,
        confidence: data.confidence,
        database_name: request.database_name,
        tables_used: data.tables_used,
        execution_result: data.execution_result,
      };
      return mapped;
    } catch (error) {
      throw getFriendlyNetworkError(error);
    }
  },

  // Index Database Schema
  async indexSchema(request: SchemaIndexRequest): Promise<SchemaIndexResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/schema/index`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to index schema'));
      }

      return response.json();
    } catch (error) {
      throw getFriendlyNetworkError(error);
    }
  },

  // Get Database Schema
  async getSchema(databaseName: string): Promise<DatabaseSchema> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/schema/${databaseName}`);

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch schema'));
      }

      return response.json();
    } catch (error) {
      throw getFriendlyNetworkError(error);
    }
  },

  // Streamed Text to SQL (SSE)
  async textToSQLStream(
    request: TextToSQLRequest,
    onEvent: (evt: { event: string; data: any }) => void,
  ): Promise<void> {
    const payload = {
      query: request.query,
      database_name: request.database_name,
      include_explanation: request.include_explanation ?? true,
      execute_query: request.execute_query ?? false,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/query/text-to-sql/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to stream SQL response'));
      }

      if (!response.body) throw new Error('Streaming not supported');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const msg of parts) {
          const lines = msg.split('\n');
          let event = 'message';
          let data = '';
          for (const line of lines) {
            if (line.startsWith('event:')) event = line.replace('event:', '').trim();
            else if (line.startsWith('data:')) data += line.replace('data:', '').trim();
          }
          try {
            const parsed = data ? JSON.parse(data) : {};
            onEvent({ event, data: parsed });
          } catch {
            onEvent({ event, data });
          }
        }
      }
    } catch (error) {
      throw getFriendlyNetworkError(error);
    }
  },
};

// Local Storage for Database Connections
export interface DatabaseConnection {
  id: string;
  name: string;
  database_name: string; // Used for API calls
  type: 'postgresql' | 'mysql' | 'sqlite' | 'mssql';
  host: string;
  port: string;
  database: string;
  username: string;
  password?: string; // Optional, for security
  connection_string?: string;
  lastUsed: string;
  indexed: boolean; // Whether schema is indexed
}

export const connectionStorage = {
  // Get all connections
  getAll(): DatabaseConnection[] {
    const stored = localStorage.getItem('db_connections');
    return stored ? JSON.parse(stored) : [];
  },

  // Get connection by ID
  getById(id: string): DatabaseConnection | null {
    const connections = this.getAll();
    return connections.find(conn => conn.id === id) || null;
  },

  // Save connection
  save(connection: DatabaseConnection): void {
    const connections = this.getAll();
    const existing = connections.findIndex(c => c.id === connection.id);
    
    if (existing >= 0) {
      connections[existing] = connection;
    } else {
      connections.push(connection);
    }
    
    localStorage.setItem('db_connections', JSON.stringify(connections));
  },

  // Delete connection
  delete(id: string): void {
    const connections = this.getAll().filter(c => c.id !== id);
    localStorage.setItem('db_connections', JSON.stringify(connections));
  },

  // Update last used timestamp
  updateLastUsed(id: string): void {
    const connections = this.getAll();
    const connection = connections.find(c => c.id === id);
    if (connection) {
      connection.lastUsed = new Date().toISOString();
      localStorage.setItem('db_connections', JSON.stringify(connections));
    }
  },

  // Mark as indexed
  markIndexed(id: string): void {
    const connections = this.getAll();
    const connection = connections.find(c => c.id === id);
    if (connection) {
      connection.indexed = true;
      localStorage.setItem('db_connections', JSON.stringify(connections));
    }
  },
};

// Build connection string helper
export function buildConnectionString(connection: Partial<DatabaseConnection>): string {
  const { type, username, password, host, port, database } = connection;

  // URL-encode credentials to handle special characters (e.g., @, :, /)
  const user = encodeURIComponent(username || "");
  const pass = encodeURIComponent(password || "");
  
  switch (type) {
    case 'postgresql':
      return `postgresql://${user}:${pass}@${host}:${port}/${database}`;
    case 'mysql':
      return `mysql+pymysql://${user}:${pass}@${host}:${port}/${database}`;
    case 'sqlite':
      return `sqlite:///${database}`;
    case 'mssql':
      return `mssql+pyodbc://${user}:${pass}@${host}:${port}/${database}?driver=ODBC+Driver+17+for+SQL+Server`;
    default:
      throw new Error('Unsupported database type');
  }
}

// Format relative time
export function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days > 1 ? 's' : ''} ago`;
}
