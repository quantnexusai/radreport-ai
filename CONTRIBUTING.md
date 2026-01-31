# Contributing to RadReport AI

Thank you for your interest in contributing to RadReport AI! This document provides guidelines and instructions for local development.

## Development Setup

### Prerequisites

- Node.js 18+ (LTS recommended)
- npm or yarn
- Git

### Getting Started

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/radreport-ai.git
   cd radreport-ai
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env.local
   ```

   For full functionality, add your API keys:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `ANTHROPIC_API_KEY`

   For UI development without API keys, set:
   ```
   NEXT_PUBLIC_DEMO_MODE=true
   ```

4. **Start the development server**

   ```bash
   npm run dev
   ```

5. **Open [http://localhost:3000](http://localhost:3000)**

## Development Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run test` | Run tests |

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   │   ├── claude/        # Claude AI endpoints
│   │   ├── facilities/    # Facilities CRUD
│   │   ├── impression-patterns/
│   │   ├── reports/       # Report generation
│   │   └── unmatched-findings/
│   ├── dashboard/         # Dashboard pages
│   └── profile/           # Profile page
├── components/
│   ├── ui/               # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── TextArea.tsx
│   │   ├── Card.tsx
│   │   ├── Tabs.tsx
│   │   └── LoadingSpinner.tsx
│   ├── dashboard/        # Dashboard components
│   │   ├── Sidebar.tsx
│   │   ├── ReportGenerator.tsx
│   │   └── admin/
│   ├── AuthModal.tsx
│   ├── DemoBanner.tsx
│   ├── Header.tsx
│   └── Footer.tsx
└── lib/
    ├── supabase.ts       # Browser Supabase client
    ├── supabase-server.ts # Server Supabase client
    ├── auth-context.tsx  # Auth context provider
    ├── demo-data.ts      # Demo mode sample data
    ├── types.ts          # TypeScript interfaces
    ├── claude.ts         # Claude API utilities
    ├── impression-matcher.ts # Pattern matching logic
    └── report-generator.ts   # Report generation orchestration
```

## Code Style

- Use TypeScript for all new code
- Follow the existing code patterns
- Use Tailwind CSS for styling
- Keep components focused and reusable
- Add proper TypeScript types

## Making Changes

1. Create a feature branch

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run linting and tests

   ```bash
   npm run lint
   npm run test
   ```

4. Commit your changes

   ```bash
   git commit -m "Add: description of your changes"
   ```

5. Push and create a pull request

   ```bash
   git push origin feature/your-feature-name
   ```

## Database Changes

If you need to modify the database schema:

1. Update `supabase/schema.sql`
2. Update the TypeScript types in `src/lib/types.ts`
3. Update the demo data in `src/lib/demo-data.ts` if applicable
4. Document the changes in your PR

## API Routes

All API routes are in `src/app/api/`. When adding new routes:

- Follow the existing pattern for error handling
- Support demo mode where appropriate
- Add proper TypeScript types for request/response
- Include authentication checks for protected routes

## Testing

Run tests with:

```bash
npm run test
```

When adding features, include appropriate tests.

## Questions?

Feel free to open an issue or contact us at ari@quantnexus.ai.
