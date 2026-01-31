# RadReport AI

AI-Powered Multimodal Radiology Report Generator. Deploy in minutes with Vercel.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fquantnexusai%2Fradreport-ai&env=NEXT_PUBLIC_SUPABASE_URL,NEXT_PUBLIC_SUPABASE_ANON_KEY,SUPABASE_SERVICE_ROLE_KEY,ANTHROPIC_API_KEY&envDescription=Get%20keys%20from%20Supabase%20and%20Anthropic&project-name=radreport-ai&repository-name=radreport-ai)

## Features

- **Structured Reports** - Generate comprehensive radiology reports with proper formatting
- **AI-Powered Analysis** - Claude AI integration for intelligent finding categorization
- **Image Analysis** - Upload CT scan images for AI-assisted visual analysis
- **Pattern Matching** - 3-tier intelligent pattern matching for consistent impressions
- **Facility Templates** - Customized technique sections based on facility equipment
- **Admin Panel** - Manage facilities, templates, and impression patterns

## Quick Start

### Step 1: Get Your API Keys

Before deploying, you'll need:

1. **Supabase** - Create a project at [supabase.com](https://supabase.com)
   - Get your Project URL and API keys from Settings > API
2. **Anthropic** - Get an API key at [console.anthropic.com](https://console.anthropic.com)

### Step 2: Deploy to Vercel

Click the deploy button above and enter your API keys when prompted.

### Step 3: Set Up Database

Run the SQL in `supabase/schema.sql` in your Supabase SQL Editor to create the required tables.

### Step 4: Done!

Your RadReport AI instance is now fully functional.

## Local Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/quantnexusai/radreport-ai.git
cd radreport-ai

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Add your API keys to .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the app.

### Demo Mode

For local UI development without API keys, the app includes sample data:

- Set `NEXT_PUBLIC_DEMO_MODE=true` in your `.env.local`
- Sample facilities, templates, and patterns are displayed
- Simulated Claude AI responses
- Full UI preview without external services

**Note:** Demo mode is for development only. Deployment requires valid API keys.

## Usage

1. **Select Study Type** - Choose Full Body, Chest, or Abdomen and Pelvis
2. **Choose Facility** - Select the imaging facility
3. **Enter Findings** - Input radiologist findings in the relevant sections
4. **Upload Image (Optional)** - Add a CT scan for AI analysis
5. **Generate Report** - Click generate to create a structured report
6. **Download** - Review and download the report as needed

## Admin Panel

The admin panel (accessible to admin users) provides:

- **Facilities Management** - Add/edit imaging facilities and technique templates
- **Impression Patterns** - Manage finding-to-impression mappings
- **Unmatched Findings** - Review findings that didn't match patterns

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase Project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (server-side) |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `NEXT_PUBLIC_DEMO_MODE` | Set to `true` for demo mode |

## Tech Stack

- **Framework** - Next.js 15 (App Router)
- **Styling** - Tailwind CSS
- **Database** - Supabase (PostgreSQL)
- **AI** - Claude API (Anthropic)
- **Hosting** - Vercel
- **Icons** - Lucide React

## Project Structure

```
radreport-ai/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── api/          # API routes
│   │   ├── dashboard/    # Dashboard pages
│   │   └── profile/      # Profile page
│   ├── components/       # React components
│   │   ├── ui/           # Reusable UI components
│   │   └── dashboard/    # Dashboard-specific components
│   └── lib/              # Utilities and configurations
│       ├── supabase.ts   # Supabase client
│       ├── claude.ts     # Claude API utilities
│       └── types.ts      # TypeScript types
├── supabase/
│   └── schema.sql        # Database schema
├── public/               # Static assets
└── package.json
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local development guidelines.

## Need Help?

For assistance with deployment, configuration, or customization, contact us at **ari@quantnexus.ai**

## License

MIT License - use freely for personal or commercial projects.
