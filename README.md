# Sarvam CommunityOS

> **Listen to your community. Understand what matters. Act on it.**

Sarvam CommunityOS is an AI-powered **Community Operations Platform** built for developer communities.

It combines a Discord-based AI assistant, Sarvam AI capabilities, community knowledge, feedback collection, human escalation, and a web dashboard into one system.

The goal is not to replace community managers. It is to give them an intelligent operating layer that can handle repetitive support, preserve community knowledge, surface unresolved issues, and turn everyday conversations into actionable community intelligence.

---

## What is CommunityOS?

CommunityOS has two sides:

### Developer-facing

A Discord assistant that can:

- Answer technical and community questions
- Search approved community knowledge
- Generate grounded responses using Sarvam AI
- Collect structured feedback
- Detect questions that cannot be confidently answered
- Create human-support escalations
- Continue escalation conversations through Discord threads

### Community-manager-facing

A web dashboard that can:

- Monitor community activity and analytics
- Manage community knowledge and documents
- Review feedback
- Review and manage escalations
- Reply to users directly through Discord escalation threads
- Track contributors and community signals
- Serve as the operational interface for the community team

---

## The Core Idea

CommunityOS follows a simple loop:

```text
                    DEVELOPER COMMUNITY
                            │
                  ┌─────────┼─────────┐
                  │         │         │
                Discord   Voice   Documents
                  │         │         │
                  └─────────┼─────────┘
                            ▼
                    ┌───────────────┐
                    │ CommunityOS   │
                    │     Agent     │
                    └───────┬───────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
             Answer      Escalate    Analyse
                │           │           │
                ▼           ▼           ▼
            Developer     Team      Dashboard
              helped    notified    insights
```

The system is designed around one question:

> **What is happening in the community, why is it happening, and what should happen next?**

---

# Key Features

## 1. AI-Powered Discord Support

Developers can ask CommunityOS questions directly in Discord.

```text
Developer
   ↓
Discord
   ↓
CommunityOS
   ↓
Knowledge Search
   ↓
Sarvam AI
   ↓
Grounded Response
```

If the available knowledge is sufficient, CommunityOS responds normally.

If the knowledge is insufficient, the system can fall back to a generated response while clearly indicating that the answer may require verification.

---

## 2. Knowledge-Grounded Answers

CommunityOS can use stored community knowledge when answering questions.

The knowledge layer is designed for content such as:

- API documentation
- FAQs
- Tutorials
- Event information
- Community guidelines
- Workshop material
- Product information
- Internal community documentation

This reduces the need for the model to rely only on general knowledge.

---

## 3. Human Escalation

CommunityOS does not pretend to know everything.

When a question cannot be confidently resolved, it can create an escalation.

```text
Developer Question
       ↓
Knowledge Search
       ↓
Insufficient Knowledge
       ↓
Fallback / Warning
       ↓
Create Escalation
       ↓
Discord Thread
       ↓
Community Team
```

Each escalation stores information such as:

- Question
- User
- Guild
- Channel
- Topic
- Bot answer
- Discord thread ID
- Status
- Conversation messages
- Creation/update timestamps

Supported statuses:

```text
open
in_progress
resolved
closed
```

### Dashboard → Discord

Community managers can reply from the dashboard.

```text
Dashboard
    ↓
FastAPI
    ↓
Discord Thread
    ↓
User receives response
    ↓
Message stored in escalation history
```

This creates a two-way support workflow instead of a dashboard that merely displays tickets.

---

## 4. Community Feedback

Developers can submit feedback through the Discord bot.

Feedback can be stored with structured information such as:

- User
- Guild
- Topic
- Category
- Feedback content
- Timestamp

The dashboard provides a dedicated interface for reviewing community feedback.

---

## 5. Community Analytics

CommunityOS exposes community data through the backend API and dashboard.

The system can be used to understand:

- Community activity
- Questions
- Feedback
- Interactions
- Contributor activity
- Escalations
- Recurring community problems

The goal is to move from individual messages to patterns and signals.

---

## 6. Contributor Intelligence

CommunityOS can track meaningful contributor activity.

Useful signals can include:

- Helpful answers
- Community participation
- Technical assistance
- Feedback
- Event participation
- Other meaningful interactions

The objective is to identify people who create value for the community, rather than simply ranking users by message count.

---

## 7. Document & Knowledge Management

Community managers can manage documents and knowledge through the dashboard.

The intended workflow is:

```text
Document
   ↓
Document Intelligence
   ↓
Extracted Content
   ↓
Processing / Chunking
   ↓
Knowledge Store
   ↓
Available to CommunityOS
```

This allows uploaded documentation to become part of the knowledge used by the assistant.

---

## 8. Sarvam AI Integration

CommunityOS is designed around Sarvam AI capabilities.

The project can integrate Sarvam capabilities for:

| Capability | Purpose |
|---|---|
| Sarvam conversational models | Response generation, reasoning and classification |
| Saaras | Speech-to-text and multilingual voice interaction |
| Bulbul | Text-to-speech |
| Document Intelligence | Document extraction and processing |

The important idea is orchestration: these capabilities are used as components of one community operations system rather than as isolated API demos.

---

# Architecture

```text
                         ┌─────────────────────┐
                         │     Developer       │
                         │      Community      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Discord       │
                         │         Bot         │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
             ┌─────────────┐                ┌─────────────┐
             │    Cogs      │                │  Sarvam AI  │
             │ ask          │                │   Client    │
             │ feedback     │                └─────────────┘
             │ escalation   │
             │ api          │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │   MongoDB   │
             │ Community   │
             │   Memory    │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │   FastAPI   │
             │     API     │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │   Next.js   │
             │  Dashboard  │
             └─────────────┘
```

---

# Project Structure

```text
SarvamCommunityOS/
│
├── backend/
│   │
│   ├── bot.py
│   ├── api.py
│   ├── database.py
│   ├── config.py
│   ├── sarvam_client.py
│   │
│   ├── cogs/
│   │   ├── api_cog.py
│   │   ├── ask.py
│   │   ├── feedback.py
│   │   └── escalation.py
│   │
│   ├── routes/
│   │   ├── analytics.py
│   │   ├── community.py
│   │   ├── contributors.py
│   │   ├── documents.py
│   │   ├── events.py
│   │   ├── feedback.py
│   │   ├── interactions.py
│   │   ├── knowledge.py
│   │   ├── stt.py
│   │   ├── support.py
│   │   └── tts.py
│   │
│   └── modules/
│       └── contributor_cog.py
│
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── analytics/
│   │   ├── contributors/
│   │   ├── knowledge/
│   │   ├── documents/
│   │   ├── feedback/
│   │   └── escalations/
│   │
│   ├── components/
│   └── lib/
│
└── README.md
```

---

# Technology Stack

## Backend

- Python
- FastAPI
- discord.py
- Pydantic

## Frontend

- Next.js
- React
- Tailwind CSS
- Lucide React

## Database

- MongoDB
- PyMongo

## AI

- Sarvam AI
- Sarvam conversational models
- Saaras
- Bulbul
- Sarvam Document Intelligence

## Communication

- Discord

---

# Discord Bot Architecture

The Discord bot uses Cogs so individual responsibilities remain isolated.

```text
CommunityOSBot
│
├── AskCog
│   └── Question answering
│
├── FeedbackCog
│   └── Feedback collection
│
├── EscalationCog
│   └── Human escalation + Discord threads
│
├── APICog
│   └── FastAPI integration
│
└── ContributorCog
    └── Contributor-related functionality
```

A shared `SarvamService` instance is initialized by the bot and exposed to the Cogs:

```python
self.sarvam = SarvamService(
    SARVAM_API_KEY
)
```

This prevents every Cog from creating its own Sarvam client.

---

# FastAPI

The backend exposes REST APIs for the dashboard.

Examples:

```text
GET    /health

GET    /api/escalations/
GET    /api/escalations/{id}

PATCH  /api/escalations/{id}/status

POST   /api/escalations/{id}/messages

DELETE /api/escalations/{id}
```

Other API modules handle areas such as:

```text
Analytics
Contributors
Knowledge
Documents
Community
Feedback
Events
Interactions
STT
TTS
```

---

# Escalation Data Flow

A complete escalation looks like this:

```text
1. Developer asks a question
              ↓
2. CommunityOS searches knowledge
              ↓
3. Knowledge is insufficient
              ↓
4. Bot provides a clearly marked fallback
              ↓
5. EscalationCog creates a Discord thread
              ↓
6. Escalation is stored in MongoDB
              ↓
7. Dashboard retrieves escalation
              ↓
8. Community manager replies
              ↓
9. FastAPI sends message to Discord thread
              ↓
10. Message is stored in MongoDB
```

This keeps the Discord conversation and dashboard conversation connected through the stored `thread_id`.

---

# Getting Started

## Prerequisites

Install:

- Python 3.11+
- Node.js 20+
- MongoDB
- A Discord application/bot
- Sarvam AI API access

---

## 1. Clone the Repository

```bash
git clone <your-repository-url>

cd SarvamCommunityOS
```

---

## 2. Backend Setup

```bash
cd backend

python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Environment Variables

Create a `.env` file in the backend:

```env
DISCORD_TOKEN=your_discord_bot_token
SARVAM_API_KEY=your_sarvam_api_key

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=communityos

CORS_ORIGINS=http://localhost:3000
```

Never commit real API keys or bot tokens.

---

## 4. Start the Backend

Start the Discord bot:

```bash
python bot.py
```

The bot loads the application Cogs and synchronizes slash commands.

The FastAPI application can be started with:

```bash
uvicorn api:app --reload --port 8000
```

---

## 5. Frontend Setup

```bash
cd frontend

npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the dashboard:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# Discord Bot Permissions

The bot requires the permissions necessary for its enabled functionality.

For escalation threads in particular, make sure the bot can:

- View channels
- Send messages
- Read message history
- Create public threads
- Send messages in threads

The bot also requires the **Message Content Intent** for message-based functionality.

---

# Security

CommunityOS handles community conversations and API credentials, so secrets should remain server-side.

### Never expose:

```text
Discord Bot Token
Sarvam API Key
MongoDB credentials
```

The browser should communicate with the backend rather than directly with Sarvam AI.

```text
Browser
   │
   ▼
FastAPI
   │
   ├── Sarvam AI
   ├── MongoDB
   └── Discord
```

Environment files should never be committed:

```text
.env
.env.local
```

---

# Design Principles

## 1. Don't hallucinate when knowledge is insufficient

If CommunityOS does not have enough information to confidently answer a question, it should make that limitation clear and provide a path to human support.

## 2. Keep humans in the loop

Escalation is a feature, not a failure.

The objective is to route difficult problems to the right people while keeping the conversation context intact.

## 3. Store useful community context

Questions, feedback, escalations, interactions, and knowledge should become structured data that can later power community intelligence.

## 4. Keep the system modular

Discord functionality belongs in Cogs.

API functionality belongs in routes.

AI integration belongs in the Sarvam service.

Dashboard functionality belongs in the frontend.

---

# Current Capabilities

| Area | Status |
|---|---|
| Discord bot | ✅ |
| Sarvam AI integration | ✅ |
| Knowledge-based Q&A | ✅ |
| Feedback collection | ✅ |
| Feedback API | ✅ |
| Escalation creation | ✅ |
| Discord escalation threads | ✅ |
| Escalation API | ✅ |
| Dashboard escalation view | ✅ |
| Dashboard → Discord replies | ✅ |
| Escalation status management | ✅ |
| Community analytics | ✅ |
| Contributor functionality | ✅ |
| Document management | ✅ |
| STT/TTS API routes | ✅ |

---

# Roadmap

## Near Term

- Improve knowledge retrieval
- Improve escalation classification
- Add richer escalation filtering
- Improve dashboard analytics
- Add real-time dashboard updates
- Improve document ingestion
- Expand multilingual interaction

## Future

- Community trend detection
- Recurring issue detection
- Community health scoring
- Automated community reports
- Contributor impact scoring
- Voice-based community support
- Cross-platform community support
- Recommendation engine for community managers

---

# Why CommunityOS?

Community platforms already contain enormous amounts of valuable information.

The problem is that most of it stays trapped inside conversations.

CommunityOS turns:

```text
Messages
   ↓
Knowledge
   ↓
Support
   ↓
Feedback
   ↓
Escalations
   ↓
Community Signals
   ↓
Action
```

Instead of only answering developers, it helps the community team understand **what developers need, where they are struggling, and what should be improved next.**

---

# Vision

The long-term vision of CommunityOS is to become an **AI-native operating layer for developer communities**.

The community manager remains the decision-maker.

CommunityOS provides the:

**context + intelligence + automation**

needed to operate a community at scale.

---

## Sarvam CommunityOS

### **Listen to your community. Understand what matters. Act on it.**
