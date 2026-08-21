---

> ## Challenge Advisor: Update & Finalize Your Project Overview
>
> > 💡 **These grey text instructions are just for you, the team's Challenge Advisor; please delete them once you have completed the steps below.**
>
> We've pre-populated this Challenge Project Overview page — which is what will be shared with your Break Through Tech student team in August — using the details from your submission form. You should have received an email inviting you to join this repo as a Collaborator, enabling you to add files and make edits.
> 
> In order for your project to be finalized and assigned to a team, please:
> 1. **Review all sections below** and update or expand any content as needed, making sure to address the SME Feedback in the section immediately below. Look for square brackets to find the places below that require additional inputs from you (e.g., "About [Company / Org Name]").
> 2. **Add your dataset** to the [data folder](data) in this repo.
> 3. **Close the Issue assigned to you in this repo** to let us know that you have made your edits and the overview page is ready for final review. You can do this by going to the _Issues_ tab in the top left section of the menu above, add a comment that says "CA review complete", and click the button to Close the Issue. 
>
> If you're unfamiliar with how to edit a page like this in GitHub, check out [this tutorial](https://ubc-lib-geo.github.io/gis-workshop-waml-template/content/handson/edit-readme.html) for a quick overview (start with step 2 and only edit this page), and [this guide](https://ubc-lib-geo.github.io/gis-workshop-waml-template/content/markdown.html) on how to use Markdown to compose text.
>
>
> ❌ Remember that this is a public repo. Do NOT include: Proprietary data, PII, API keys, credentials, or anything confidential.

---

## 📋 BTT Internal Evaluation Notes

| Check | Status | Notes |
|-------|--------|-------|
| Python Compatibility | GREEN | The project's tech stack is centered on Python, particularly due to the use of RAG techniques and NLP tools which are available in Python libraries. |
| Data Readiness | YELLOW | Data is publicly available and under 1GB, but will require cleaning and preprocessing for effective use. This introduces some risks in the initial phases of the project. |
| Resource Check | GREEN | The project is designed to be feasible using the free tier of Google Colab, which is accessible and eliminates hardware constraints. |

**Student Fit Score:** 7/10  
**Technical Depth Score:** 8/10  
**Overall Recommendation:** REVISE

**Advisor Feedback Draft:**
The project presents a viable opportunity for students to engage with the complexities of NLP and model evaluation. However, they must be prepared for potential delays in data processing and a need for rigorous evaluation against success metrics.

---

# AI Research Intelligence Agent for Business Insight Translation

**Company / Org:** KPMG  
**Challenge Advisor:** Chris Jambor, cjambor@kpmg.com 

**AI Coach:** Alexandra Ladyzhensky, alexandra.ladyzhensky@breakthroughtech.org

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


> **Note for the team:** Please create a GitHub Projects board in this repository to break these milestones into weekly tasks. We've included an example breakdown below. Go to the **Projects** tab → **New project** → Choose **Board** → Add columns for each month.

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

**Name and Source:** Publicly available AI research data from arXiv, specific to Artificial Intelligence   
**Format:** Categorical and Text, primarily in PDF format  
**Size:** under 1gb  
**Location:** arXiv Artificial Intelligence Research: https://arxiv.org/list/cs.AI/recent


### Key Details
arXiv (pronounced "archive") is a free online platform and open-access archive. Researchers use it to share **early versions of scientific papers—called preprints—before formal peer review.** It covers physics, mathematics, computer science, statistics, quantitative biology, quantitative finance, and economics.

---

## 🛠️ Suggested Approach

**ML Problem Type:** NLP / Retrieval-augmented Generation

**Note to BTT AI Coaches and Fellows:** 
We propose the following approaches, but work with your AI coaches to determine the best approach for your team:
1.	Use the provided link to the arXiv website with the repository of AI research papers and determine a way to build an agent that navigates to the site, evaluates all the links, downloads the files to analyze the content, and then generate the insights, etc.
2.	Download our sample subset of the research papers to ground your RAG solution and then build an agent that analyzes the content and generates cited insights. 


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
* **Preferred** KPMG Email; please copy your teammates and AI Studio Coach
* I am on the team's channel within Break Through Tech’s Discord space, but email is better.
* Note: Regardless of channel, I will aim to respond within 48 hours. Please reach out to your AI Studio Coach with urgent questions.
* Optional: Request a team check-in on Zoom if things go off the rails


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
