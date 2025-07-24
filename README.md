# SentientEcho 🔍🧠

**Real Reddit & Twitter Posts for Any Query**

SentientEcho is an intelligent agent that responds to natural language queries with actual Reddit and Twitter posts, powered by AI summarization and built for seamless SentientChat integration.

## 🚀 Features

- **Real Post Retrieval**: Fetches actual Reddit and Twitter content, not just summaries
- **AI-Powered Processing**: Uses Sentient Dobby Llama 3 70B for query understanding and summarization
- **Smart Filtering**: Supports subreddit, time range, and engagement filters
- **Sentiment Analysis**: Detects positive, negative, and neutral sentiment in posts
- **SentientChat Native**: Built with Sentient Agent Framework for perfect integration
- **Zero Cost**: Uses only free APIs and open-source tools

## 🎯 Example Queries

- *"What do Redditors say about Coinbase's recent outage?"*
- *"Latest Twitter sentiment on ETH ETFs?"*
- *"Best subreddit discussions on productivity tools in 2025?"*
- *"How is the gaming community reacting to GTA 6 leaks?"*

## 🛠️ Architecture

```
User Query → SentientChat → SentientEcho Agent
    ↓
1. Query Preprocessing (Dobby AI)
    ↓
2. Multi-Source Search (Reddit + Twitter)
    ↓
3. Content Processing & Ranking
    ↓
4. Optional AI Summary Generation
    ↓
Response → SentientChat → User
```

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Panchu11/sentientecho.git
cd sentientecho

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys
```

## 🔧 Configuration

Set up your API keys in `.env`:

```env
FIREWORKS_API_KEY=your_fireworks_key
FIREWORKS_MODEL_ID=accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new
SERPER_API_KEY=your_serper_key
JINA_AI_API_KEY=your_jina_key
```

## 🚀 Usage

### Local Development
```bash
python src/main.py
```

### SentientChat Integration
The agent exposes a `/assist` endpoint compatible with Sentient Agent API format.

## 🧩 Agent Capabilities

- **Reddit Fetch**: Search Reddit posts and comments
- **Twitter Fetch**: Real-time Twitter/X content retrieval  
- **Real Post Context**: Actual post content with metadata
- **AI Summary**: Optional Dobby-powered summaries
- **Query Filters**: Subreddit, time, engagement filtering

## 🔗 SentientChat Integration

**Agent Name**: SentientEcho  
**Description**: Answers any query using real Reddit and Twitter posts. Cuts through noise with actual public sentiment and AI summaries.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Built for the Sentient Foundation ecosystem. Contributions welcome!

---

*Powered by Sentient Dobby Llama 3 70B • Built with Sentient Agent Framework*
