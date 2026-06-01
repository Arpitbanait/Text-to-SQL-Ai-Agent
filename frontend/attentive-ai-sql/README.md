# Text-to-SQL Frontend

A modern, responsive React frontend application for the Text-to-SQL system. Built with React, TypeScript, Vite, and Shadcn UI components.

## Features

- 🎨 Modern UI with Shadcn components and Tailwind CSS
- 🌓 Dark/Light theme support
- 📱 Fully responsive design
- ⚡ Fast development with Vite
- 🎯 Type-safe with TypeScript
- 🔄 Real-time query generation
- 📊 SQL syntax highlighting
- 🚀 Optimized production builds

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn UI + Radix UI
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Form Handling**: React Hook Form + Zod
- **Icons**: Lucide React

## Prerequisites

- Node.js 18.x or higher
- npm, yarn, pnpm, or bun

## Installation & Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend/attentive-ai-sql
```

### 2. Install Dependencies

**Using npm:**
```bash
npm install
```

**Using yarn:**
```bash
yarn install
```

**Using pnpm:**
```bash
pnpm install
```

**Using bun:**
```bash
bun install
```

### 3. Environment Configuration

Create a `.env` file in the `frontend/attentive-ai-sql` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=Text-to-SQL Generator
```

### 4. Run Development Server

**Using npm:**
```bash
npm run dev
```

**Using yarn:**
```bash
yarn dev
```

**Using pnpm:**
```bash
pnpm dev
```

**Using bun:**
```bash
bun run dev
```

The application will be available at `http://localhost:5173`

### 5. Build for Production

**Build:**
```bash
npm run build
```

The production build will be created in the `dist/` directory.

**Preview Production Build:**
```bash
npm run preview
```

## Project Structure

```
frontend/attentive-ai-sql/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   │   └── ui/         # Shadcn UI components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions
│   ├── pages/          # Page components
│   ├── services/       # API service layer
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── index.html          # HTML template
├── vite.config.ts      # Vite configuration
├── tailwind.config.ts  # Tailwind configuration
├── tsconfig.json       # TypeScript configuration
└── package.json        # Dependencies and scripts
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Connecting to Backend

Ensure the backend API is running on `http://localhost:8000` or update the `VITE_API_BASE_URL` in your `.env` file.

The frontend expects the following API endpoints:

- `POST /api/query/generate` - Generate SQL from natural language
- `GET /api/schema/{database_name}` - Fetch database schema
- `GET /api/health` - Health check

## Key Features

### Query Interface
- Natural language input
- Database selection
- Real-time SQL generation
- Copy to clipboard functionality

### Schema Viewer
- Browse database schemas
- View table structures
- Explore relationships

### Theme Toggle
- Light/Dark mode support
- Persistent theme preference
- System theme detection

## Customization

### Adding New Components

Use Shadcn CLI to add new components:

```bash
npx shadcn@latest add <component-name>
```

Example:
```bash
npx shadcn@latest add button
npx shadcn@latest add dialog
```

### Tailwind Configuration

Modify `tailwind.config.ts` to customize:
- Colors
- Fonts
- Spacing
- Breakpoints

### Theme Customization

Edit `src/index.css` to modify CSS variables for light/dark themes.

## Building for Production

### Optimize Build

1. **Code Splitting**: Vite automatically handles code splitting
2. **Tree Shaking**: Unused code is removed
3. **Minification**: Production builds are minified
4. **Asset Optimization**: Images and assets are optimized

### Deployment

**Deploy to Vercel:**
```bash
npm install -g vercel
vercel
```

**Deploy to Netlify:**
```bash
npm install -g netlify-cli
netlify deploy --prod
```

**Deploy with Docker:**

Create a `Dockerfile` in the frontend directory:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t text2sql-frontend .
docker run -p 80:80 text2sql-frontend
```

## Troubleshooting

### Port Already in Use
If port 5173 is in use, Vite will automatically use the next available port.

### Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf .vite`

### API Connection Issues
- Verify backend is running on correct port
- Check CORS settings on backend
- Verify `VITE_API_BASE_URL` in `.env`

### Type Errors
- Run `npm run build` to check for TypeScript errors
- Update TypeScript types if needed

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimization

- Lazy loading of routes
- Code splitting by route
- Image optimization
- CSS purging with Tailwind
- Bundle size analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
