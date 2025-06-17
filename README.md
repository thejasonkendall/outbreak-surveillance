# 🦠 Public Health Surveillance System

A Real-time global public health monitoring and intelligence analysis.

## 🎯 Overview

This system combines news monitoring, AI analysis, and real-time dashboards to provide public health intelligence on worldwide events. It uses Claude AI to analyze news articles like a public health professional and generates actionable health intelligence.

## 🏗️ Production Infrastructure

- ✅ Auto Scaling Group with load balancer
- ✅ Multi-AZ RDS PostgreSQL database
- ✅ ECR repositories for container images
- ✅ VPC with public/private subnets
- ✅ Security groups properly configured
- ✅ ALB with path-based routing

## 🚀 CI/CD Pipeline

- ✅ GitLab CI/CD with automated builds
- ✅ AWS CodeDeploy for zero-downtime deployments
- ✅ Docker multi-container setup (API + Dashboard)
- ✅ SSM Parameter Store for secure secrets management

## 🤖 AI Intelligence System

- ✅ NewsAPI integration for real-time health news
- ✅ Claude AI analysis extracting structured intelligence
- ✅ Confidence scoring and significance assessment
- ✅ Smart categorization (topics, locations, stakeholders)

## 💻 Full-Stack Application

- ✅ FastAPI backend with REST endpoints
- ✅ Beautiful responsive dashboard with filtering/search
- ✅ Real-time health intelligence display
- ✅ PostgreSQL database with proper indexing

## 🏗️ Architecture

```
📰 NewsAPI → 🤖 Claude AI → 🗄️ Postgres DB → 🔌 FastAPI → 🖥️ Dashboard
```

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Load Balancer                │
│                         (AWS ALB)                          │
└─────────────────┬───────────────────┬──────────────────────┘
                  │                   │
         ┌────────▼─────────┐ ┌───────▼─────────┐
         │   EC2 Instance 1 │ │  EC2 Instance 2 │
         │                  │ │                 │
         │ ┌──────────────┐ │ │ ┌─────────────┐ │
         │ │ API Container│ │ │ │API Container│ │
         │ │ + Dashboard  │ │ │ │+ Dashboard  │ │
         │ └──────────────┘ │ │ └─────────────┘ │
         └──────────────────┘ └─────────────────┘
                  │                   │
                  └─────────┬─────────┘
                           │
              ┌─────────────▼─────────────┐
              │     RDS PostgreSQL        │
              │    (Multi-AZ for HA)      │
              └───────────────────────────┘
                           │
              ┌─────────────▼─────────────┐
              │   EC2 Instance 3          │
              │ ┌─────────────────────────┐│
              │ │  Data Collector        ││
              │ │  (Scheduled via Cron)  ││
              │ └─────────────────────────┘│
              └───────────────────────────┘
```

**Data Pipeline Flow:**

1. **NewsAPI** fetches outbreak-related news articles
2. **Claude AI** analyzes articles and extracts structured intelligence 
3. **Supabase** stores outbreak data with AI-generated summaries
4. **FastAPI** serves data through REST endpoints
5. **Dashboard** displays live outbreak intelligence

## 🚀 Features

- **AI-Powered Analysis**: Claude AI reads news articles like a human epidemiologist
- **Real-time Intelligence**: Live dashboard with outbreak monitoring
- **Smart Extraction**: Extracts disease, location, severity, and case counts
- **Confidence Scoring**: AI provides confidence levels for each analysis
- **Intelligence Summaries**: Natural language explanations of outbreak significance
- **Source Linking**: Direct links to original news articles

## 📋 Prerequisites

- Python 3.8+
- Supabase account (free tier available)
- NewsAPI key (free tier: 1000 requests/day)
- Anthropic Claude API key
- Modern web browser

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd outbreak-surveillance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install requests pandas python-dotenv fastapi uvicorn supabase anthropic
pip freeze > requirements.txt
```

### 2. Configuration

Create `.env` file:

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
NEWS_API_KEY=your_newsapi_key
ANTHROPIC_API_KEY=your_claude_api_key
```

### 3. Database Setup

Run this SQL in your SQL Editor:

```sql
CREATE TABLE outbreaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    disease_name VARCHAR NOT NULL,
    location_country VARCHAR NOT NULL,
    location_region VARCHAR,
    outbreak_date DATE NOT NULL,
    reported_cases INTEGER,
    reported_deaths INTEGER,
    outbreak_status VARCHAR DEFAULT 'active',
    source_url TEXT,
    source_organization VARCHAR,
    severity_level VARCHAR,
    intelligence_summary TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔧 Detailed Setup

### API Keys Setup

#### Supabase

1. Go to [supabase.com](https://supabase.com)
2. Create account and new project
3. Get URL and anon key from Settings → API

#### NewsAPI  

1. Go to [newsapi.org](https://newsapi.org)
2. Sign up for free account
3. Get API key from dashboard

#### Claude AI

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create account and add billing
3. Generate API key
4. Add $5-10 credits (very affordable)

## 🎮 Usage

### Operation

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Collect outbreak intelligence
python data-pipeline/claude_news_collector.py

# 3. Start API server
python api/main.py

# 4. Open dashboard/index.html in browser
```

### API Endpoints

```bash
# Get all outbreaks
GET http://localhost:8000/outbreaks

# Get outbreak summary statistics  
GET http://localhost:8000/outbreaks/summary

# Health check
GET http://localhost:8000/
```

## 📊 Dashboard Features

The web dashboard displays:

- **Live outbreak cards** with disease, location, and case counts
- **AI intelligence summaries** explaining outbreak significance
- **Severity levels** assessed by Claude AI
- **Confidence scores** for each analysis
- **Direct links** to source news articles
- **Real-time updates** as new outbreaks are detected

## 🤖 AI Intelligence

Claude AI analyzes each news article and extracts:

- **Disease identification** and pathogen type
- **Geographic location** (country and region)
- **Case counts** and fatality rates
- **Severity assessment** with reasoning
- **Public health response** level
- **Intelligence summary** in natural language
- **Confidence scoring** for reliability

Example AI Summary:
> *"Significant cholera outbreak in Sudan with confirmed cases across multiple states amid humanitarian crisis, requiring immediate international attention"*

## 📁 Project Structure

```
outbreak-surveillance/
├── data-pipeline/
│   ├── news_collector.py          # NewsAPI integration
│   ├── ai_analyzer.py             # Claude AI analysis
│   ├── claude_news_collector.py   # Combined news + AI pipeline
├── api/
│   └── main.py                    # FastAPI REST endpoints
├── dashboard/
│   └── index.html                 # Web dashboard
├── .env                          # Configuration (not in git)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔍 Troubleshooting

### Common Issues

**No outbreaks found:**

```bash
# Increase search timeframe
# In claude_news_collector.py, change:
articles = news_collector.fetch_outbreak_news(days_back=31, max_articles=15)
```

**Dashboard not updating:**

```bash
# Verify API is running
curl http://localhost:8000/outbreaks
```

### Debug  

```bash
# Check API endpoints
curl http://localhost:8000/outbreaks
curl http://localhost:8000/outbreaks/summary
```

## 🚀 Deployment

### Development

```bash
# API server
python api/main.py

# Autonomous agent
python data-pipeline/autonomous_agent.py
```

### Production - Coming soon!

## 🔐 Security Notes

- Keep `.env` file private (added to `.gitignore`)
- Use environment variables for all API keys
- Supabase Row Level Security policies recommended for production
- Consider rate limiting for public deployments

## 🎯 Use Cases

- **Public Health Surveillance**: Real-time outbreak monitoring
- **Research**: Disease pattern analysis and trend identification  
- **Policy Making**: Evidence-based health emergency responses
- **Education**: Teaching outbreak surveillance concepts
- **Portfolio Project**: Demonstrating AI + health tech skills

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

This project is released into the public domain under the Unlicense - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Claude AI** for intelligent news analysis
- **Supabase** for real-time database infrastructure
- **NewsAPI** for global news coverage
- **WHO** and **CDC** for outbreak classification guidance

## 📞 Support

For questions or issues:

1. Check the troubleshooting section above
2. Review API documentation at `http://localhost:8000/docs`

---

**Built with ❤️ for global health surveillance and disease outbreak prevention.**