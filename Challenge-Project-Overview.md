# AI Research Intelligence Agent for Business Insight Translation

**Company / Org:** KPMG  
**Challenge Advisor:** Allison Tatterson, atatterson@KPMG.com
**AI Coach:** Rashidah Carr, rashidah.carr@breakthroughtech.org
**Program:** Break Through Tech AI Studio - Fall 2026

---

## 🏢 About KPMG

KPMG is a global leader in audit, tax, and advisory services, providing insights and expertise to a diverse clientele across various industries. Our commitment to innovation drives us to integrate technology into our solutions, enhancing business performance and fostering success.

---

## 🎯 The Challenge

### Project Summary
In this project, you will use publicly available AI research data (e.g., arXiv papers and metadata) and retrieval-augmented generation (RAG) techniques with large language models to build an agent that retrieves relevant research, summarizes key findings, and translates them into business-relevant insights. This will help our organization address the challenge of efficiently monitoring and operationalizing the rapidly growing volume of AI research. Abhinav Raghunathan will serve as the KPMG business owner for the project, responsible for guiding business relevance, success criteria, and stakeholder feedback.

### Success Criteria

_Success will be measured based on:_
- Retrieval relevance: Ability to return appropriate research papers for a given query
- Summary quality: Accuracy and clarity of synthesized research insights
- Business usefulness: Extent to which outputs translate technical content into actionable business implications
- Human evaluation: Validation by KPMG stakeholders reviewing relevance and accuracy of outputs

_Human-in-the-loop checkpoint:_ 
- KPMG stakeholders will review retrieved sources, summaries, and business implications before outputs are used for internal decision-making, thought leadership, or client-facing discussions.

_A successful outcome will be:_
- A working prototype that enables natural-language querying of AI research and produces summarized, business-relevant outputs with citations
- Documented evaluation approach and results
- Demonstrated applicability for internal enablement and client conversations
- A final solution package that includes prototype documentation, evaluation results, scope limitations, and a final presentation suitable for stakeholder review.

### Stretch Goals

Potential stretch goals may include:   
- Add draft newsletter or report-generation capability for human review (e.g., research briefs or POV drafts, not publication-ready outputs)
- Introduce multi-source synthesis across research repositories
- Implement relevance ranking or personalization based on user intent
- Develop a simple front-end interface for stakeholder interaction
- Incorporate evaluation benchmarking dataset for improved retrieval accuracy

Stretch goals to be maintained within prototype scope; exclude production deployment, foundation-model fine-tuning, autonomous multi-agent orchestration, and use of PII, regulated, internal, or client data.

### Project Milestones

Use these milestones to guide your work. Your team will create a **GitHub Projects board** to track tasks within each milestone.

| Month | Milestone | Key Activities |
|---|---|---|
| September | Foundation & Baseline RAG Development | • Data exploration and preprocessing<br>• Define evaluation framework and benchmark queries<br>• Develop baseline retrieval pipeline (RAG setup) |
| October | Pipeline Development & Evaluation | • Implement retrieval + summarization pipeline<br>• Develop prompt engineering approach for business translation<br>• Begin evaluation (relevance and accuracy testing) |
| November | Solution Refinement, User Experience & Final Delivery | • Refine model outputs and improve ranking/relevance<br>• Build lightweight user interface or interaction layer<br>• Document solution and prepare final presentation |

> **Note for the team:** Please create a GitHub Projects board in this repository to break these milestones into weekly tasks. Go to the **Projects** tab → **New project** → Choose **Board** → Add columns for each month.

| Month	| Week | Weekly Tasks |
|---|---|---|
| September	| Week 1	| Project kickoff, review challenge requirements, identify data sources, set up development environment and repository structure |
| September	| Week 2	| Conduct exploratory data analysis (EDA), assess data quality, identify gaps and preprocessing needs |
| September |	Week 3	| Clean and preprocess data, create data ingestion pipeline, document data preparation approach
| September	| Week 4	| Define evaluation framework, establish benchmark questions/queries, build and test baseline RAG retrieval pipeline
| October	| Week 5	| Implement retrieval pipeline improvements and integrate summarization capabilities
| October	| Week 6	| Develop and test end-to-end retrieval + summarization workflow, evaluate initial outputs
| October	| Week 7	| Design and implement prompt engineering strategy for translating technical outputs into business-friendly insights
| October	| Week 8	| Conduct evaluation testing for relevance, accuracy, and completeness; document findings and improvement opportunities
| November	| Week 9	| Refine prompts, retrieval ranking, and relevance mechanisms based on evaluation results
| November	| Week 10	| Improve model outputs, optimize user experience, and begin development of lightweight user interface or interaction layer
| November	| Week 11	| Finalize UI/interaction layer, perform user testing, complete technical and business documentation
| November	| Week 12	| Prepare final presentation, create demo materials, conduct final testing, and package solution for submission

---

## 📊 Dataset

**Name and Source:** Publicly available AI research data from arXiv   
**Format:** Categorical and Text, primarily in PDF format  
**Size:** under 1gb  
**Location:** arXiv Artificial Intelligence Research: https://arxiv.org/list/cs.AI/recent

### Key Details
arXiv (pronounced "archive") is a free online platform and open-access archive. Researchers use it to share early versions of scientific papers—called preprints—before formal peer review. It covers physics, mathematics, computer science, statistics, quantitative biology, quantitative finance, and economics.

---

## 🛠️ Suggested Approach

**ML Problem Type:** NLP / Retrieval-augmented Generation

**Note to BTT AI Coaches and Fellows:** We propose the following approaches, but work with your AI coaches to determine the best approach for your team:
1. Use the provided link to the arXiv website with the repository of AI research papers and determine a way to build an agent that navigates to the site, evaluates all the links, downloads the files to analyze the content, and then generate the insights, etc.
2. Download our sample subset of the research papers to ground your RAG solution and then build an agent that analyzes the content and generates cited insights.

**Recommended Libraries:**
- [e.g., pandas, scikit-learn, TensorFlow, Hugging Face]

**Evaluation Metrics:**
- [e.g., Accuracy, Precision/Recall, RMSE, BLEU score]

---

## 📚 Resources to Get Started

The following resources will help your team understand the problem space and potential technical approaches for this project:

**Background Reading:**
- [e.g., Link to an article or blog post about the problem domain]
- [e.g., Link to an industry report or case study]

**Technical Tutorials:**
- [e.g., Link to a free tutorial on the ML technique(s) involved]
- [e.g., Link to documentation for a key library or tool]

**Code Examples:**
- [e.g., Link to a relevant GitHub repo]
- [e.g., Link to a sample implementation or starter code]

**Other:**
- [Links to any additional resources — e.g., papers, videos, podcasts, etc.]

*Feel free to explore beyond these, and share anything interesting you find with me!*

---

## 🤝 How We'll Work Together

**Official check-ins:** During our biweekly 45-minute AI Studio Lab Section meeting block (2nd and 4th week of every month)

 **Other ways to reach out to me with questions:** 
* **Preferred** Email atatterson@kpmg.com; please copy your teammates and AI Studio Coach.
* Note that I am **not** on the team's channel within Break Through Tech Discord space. 
* Note: I will aim to respond within 48 hours. Please reach out to your AI Studio Coach with urgent questions.
* Optional: Request a team check-in on Zoom if things go off the rails. 

> 💡 **Challenge Advisor: Please update the above based on your availability and preference. If you are not able to answer questions or meet with fellows outside of the biweekly Lab Section check-ins, simply write in "N/A (only available during the official check-in times)"**

**Recommended free coding / collaboration tools**
* […]
* […]

---

## 🚀 Getting Started

1. **Review this overview document** and note any questions for our first meeting
2. **Begin reviewing the dataset** using the link above
3. **Read the GitHub Projects documentation** [here](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)

I’m excited to work with you!


---

## ❓ Questions?

Please bring any questions to our first meeting during the week of August 24th (Break Through Tech’s Bridge to Studio - Session C). 
