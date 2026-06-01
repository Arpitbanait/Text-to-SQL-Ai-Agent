import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Database, Sparkles, Zap, Shield, ArrowRight } from "lucide-react";
import AnimatedBackground from "@/components/AnimatedBackground";

const Landing = () => {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <AnimatedBackground />
      
      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 lg:px-12">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/50 flex items-center justify-center glow-cyan">
            <Database className="w-5 h-5 text-primary" />
          </div>
          <span className="text-xl font-bold text-foreground">QueryAI</span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login">
            <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
              Login
            </Button>
          </Link>
          <Link to="/signup">
            <Button className="glow-cyan bg-primary text-primary-foreground hover:bg-primary/90">
              Get Started
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-6 pt-20 pb-32 lg:pt-32">
        <div className="animate-fade-in-up text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border-glow-cyan mb-8">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm text-muted-foreground">AI-Powered SQL Generation</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold mb-6 leading-tight">
            <span className="text-foreground">Transform </span>
            <span className="text-primary glow-text-cyan">Natural Language</span>
            <br />
            <span className="text-foreground">into </span>
            <span className="text-secondary glow-text-purple">SQL Queries</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            Connect your databases, ask questions in plain English, and let AI generate 
            perfect SQL queries instantly. No SQL expertise required.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup">
              <Button size="lg" className="glow-cyan bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-6 text-lg group">
                Start For Free
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button size="lg" variant="outline" className="border-border/50 hover:border-primary/50 hover:bg-primary/10 px-8 py-6 text-lg">
                View Demo
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto w-full animate-fade-in" style={{ animationDelay: "0.3s" }}>
          <FeatureCard
            icon={Database}
            title="Multi-Database Support"
            description="Connect PostgreSQL, MySQL, and SQLite databases seamlessly"
            glowClass="border-glow-cyan"
          />
          <FeatureCard
            icon={Zap}
            title="Instant Generation"
            description="Get accurate SQL queries in seconds with AI-powered analysis"
            glowClass="border-glow-purple"
          />
          <FeatureCard
            icon={Shield}
            title="Secure & Private"
            description="Your credentials are encrypted and never leave your control"
            glowClass="border-glow-cyan"
          />
        </div>

        {/* Preview Window */}
        <div className="mt-20 w-full max-w-4xl mx-auto animate-fade-in-up" style={{ animationDelay: "0.5s" }}>
          <div className="glass rounded-xl p-1 border-glow-cyan">
            <div className="bg-card rounded-lg overflow-hidden">
              {/* Window Header */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-border/50">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-destructive/60" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                  <div className="w-3 h-3 rounded-full bg-green-500/60" />
                </div>
                <span className="text-xs text-muted-foreground ml-2">QueryAI Chat</span>
              </div>
              {/* Chat Preview */}
              <div className="p-6 space-y-4">
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">U</div>
                  <div className="glass rounded-lg px-4 py-2 max-w-md">
                    <p className="text-sm">Show me all users who signed up this month</p>
                  </div>
                </div>
                <div className="flex gap-3 justify-end">
                  <div className="bg-primary/10 border border-primary/30 rounded-lg px-4 py-3 max-w-lg">
                    <pre className="text-sm font-mono text-primary">
{`SELECT * FROM users
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
ORDER BY created_at DESC;`}
                    </pre>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-primary" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 py-8 text-center text-sm text-muted-foreground">
        <p>© 2024 QueryAI. Built with AI-powered intelligence.</p>
      </footer>
    </div>
  );
};

interface FeatureCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  glowClass: string;
}

const FeatureCard = ({ icon: Icon, title, description, glowClass }: FeatureCardProps) => (
  <div className={`glass rounded-xl p-6 ${glowClass} hover:scale-105 transition-transform duration-300`}>
    <div className="w-12 h-12 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center mb-4">
      <Icon className="w-6 h-6 text-primary" />
    </div>
    <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
    <p className="text-sm text-muted-foreground">{description}</p>
  </div>
);

export default Landing;
