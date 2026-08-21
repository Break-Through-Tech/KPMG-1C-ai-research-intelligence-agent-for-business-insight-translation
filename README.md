# AI Research Intelligence Agent for Business Insights

## Project Highlights

- Develop a Retrieval-Augmented Generation (RAG) system that enables users to query a corpus of AI research papers using natural language and receive business-oriented insights with source citations.
- Address the challenge of rapidly scaling AI research volume, which makes manual monitoring, synthesis, and business translation increasingly difficult for enterprise teams.
- Design an AI-powered workflow that augments existing research and knowledge management processes by accelerating discovery, retrieval, and summarization of relevant AI research.
- Generate actionable, business-friendly recommendations to support internal enablement, thought leadership, and client-facing conversations.
- Incorporate human review checkpoints to support responsible AI practices, ensuring research summaries and recommendations are validated before use in business decision-making.

## 👩🏽‍💻 Setup and Installation

*Included as informational resources, but not relevant to the challenge as coaches will own the repo.*

### Clone the Repository

```bash
git clone https://github.com/<your-organization>/<repository-name>.git
cd <repository-name>
```

### Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Download and Prepare Data

The project uses publicly available AI research data sources, including arXiv papers and associated metadata such as titles, abstracts, authors, publication dates, and categories.

**Source:** [https://arxiv.org/list/cs.AI/recent](https://arxiv.org/list/cs.AI/recent) — arXiv Artificial Intelligence research papers

**Note to BTT AI Coaches and Fellows:**

We propose the following approaches, but are open to others:

1. Use the provided link to the arXiv website with the repository of AI research papers and determine a way to build an agent that navigates to the site, evaluates all the links, downloads the files to analyze the content, and then generate the insights, etc.
2. Download a subset of the research papers to create a sample corpus to ground your RAG solution and then build an agent that analyzes the content and generates cited insights.

Place downloaded datasets in the `/data` directory.

### Run the Application *(confirm with coach)*

```bash
python app.py
```

Or run the notebook:

```bash
jupyter notebook
```

## 🏗️ Project Overview

### Break Through Tech AI Program

This project was developed as part of the Break Through Tech AI Studio program in collaboration with KPMG. The project was designed to provide students with hands-on experience applying machine learning, generative AI, and retrieval systems to a real-world business challenge.

### Host Company and Business Objective

The project was sponsored by KPMG's Trusted AI Team. The objective was to create an AI-powered research intelligence agent capable of identifying, retrieving, and synthesizing relevant AI research findings into actionable business insights.

Today, AI researchers and business professionals often spend significant time manually searching for papers, reviewing abstracts, comparing findings, and summarizing information. This manual process limits the organization's ability to rapidly capitalize on emerging AI developments. The proposed solution augments this workflow by enabling faster discovery and interpretation of relevant research.

### Business Impact

By streamlining access to relevant AI research, this solution can:

- Reduce time spent monitoring AI developments.
- Improve organizational awareness of emerging AI opportunities and risks.
- Support client-facing conversations with evidence-backed insights.
- Accelerate internal knowledge sharing and thought leadership development.

## 📊 Data Exploration

### Dataset Description

The project leverages publicly available AI research datasets, primarily sourced from arXiv and related research repositories. Data includes:

- Research paper titles
- Abstracts
- Authors
- Publication dates
- Subject categories
- Associated metadata

### Data Preparation

Preprocessing activities may include:

- Metadata normalization
- Text cleaning
- Abstract parsing
- Document chunking for retrieval
- Embedding generation for semantic search

These preprocessing steps were intentionally lightweight to allow focus on retrieval quality and user experience rather than extensive ETL work.

### Exploratory Data Analysis (EDA)

Potential analyses include:

- Distribution of papers by research category
- Publication trends over time
- Most-cited topics
- Emerging AI themes
- Author and institution frequency analysis

### Suggested Visualizations

- Topic distribution charts
- Publication trend line graphs
- Category heatmaps
- Semantic embedding visualizations
- Word clouds of research abstracts

## 🧠 Model Development

### Solution Architecture

The project centers on a Retrieval-Augmented Generation (RAG) architecture that:

1. Accepts a natural language user query.
2. Searches a research corpus for relevant papers.
3. Retrieves supporting documents.
4. Generates summaries and recommendations.
5. Provides source citations with outputs.

### Models and Technologies

**Start here:** Teams can use HuggingFace as a repository for open-source models. Open-source vector databases are also a possibility.

Other potential technologies could include:

- Azure OpenAI
- OpenAI embedding models
- Vector databases
- Semantic search retrieval pipelines
- Large Language Models for summarization

### Training and Evaluation Strategy

Because no definitive ground-truth dataset exists for determining the "best" research recommendations, evaluation focuses on:

- Retrieval relevance
- Citation quality
- Summary accuracy
- Human stakeholder reviews
- Business usefulness

A benchmark set of representative user questions can be used alongside expert evaluation to assess performance.

## 📈 Results & Key Findings

### Prototype Outcomes

A successful project outcome includes:

- A working conversational research assistant.
- Retrieval of relevant papers with citations.
- Business-oriented summaries and recommendations.
- Documentation of system design and evaluation methodology.

### Human-in-the-Loop Evaluation

To support responsible AI practices, all generated recommendations are reviewed by a human evaluator prior to use in decision-making, client communications, or thought leadership materials.

### Suggested Evaluation Metrics

- Precision@K & Recall@K
- **Q&A Accuracy:** how well did the solution answer questions? Typical RAG metrics (Context Relevance, Faithfulness, Answer Relevance)
- **Citation Accuracy:** how well did the solution cite proper sources?
- **Summarization Scoring/User Satisfaction Ratings:** how well did the solution summarize papers?
- **Qualitative Product Design/Human Relevance scoring:** how well was the UI/UX designed? How fast did it feel?

### Suggested Visualizations

- Retrieval performance charts
- Relevance scoring distributions
- Evaluation score dashboards
- Citation coverage analysis
- User feedback summary charts

## 🚀 Next Steps

### Current Limitations

- Reliance on publicly available research content.
- Limited availability of labeled ground-truth recommendation datasets.
- Human evaluation required for quality validation.
- Prototype scope limited to research retrieval and summarization.

### Future Enhancements

- Expand corpus coverage beyond arXiv.
- Incorporate enterprise knowledge repositories.
- Improve recommendation ranking quality.
- Add personalized research alerts.
- Develop richer evaluation benchmarks.
- Explore agent-driven multi-step retrieval workflows while maintaining human oversight.

## 📝 License

This project is licensed under an MIT License. *(confirm with coaches)*

## 📄 References

- arXiv Research Repository
- Azure OpenAI Documentation
- Retrieval-Augmented Generation (RAG) Research Literature
- Break Through Tech AI Studio Program Resources

## 🙏 Acknowledgements

Special thanks to:

- Abhinav Raghunathan, KPMG AI + Data Labs, Technical Business Expert and lead Challenge Advisor, for project guidance, evaluation support, and domain expertise.
- Agnieszka Jeter and the KPMG Trusted AI Team for sponsoring the project and providing business context.
- Break Through Tech AI Studio leadership, teaching assistants, and program staff for mentorship and technical support.
- All project stakeholders who contributed feedback throughout the project lifecycle.

This project demonstrates how GenAI and Retrieval-Augmented Generation can help organizations transform large volumes of research into actionable business intelligence while maintaining responsible AI governance practices.
