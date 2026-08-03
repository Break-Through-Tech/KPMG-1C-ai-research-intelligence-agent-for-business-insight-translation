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
**Challenge Advisor:** Allison Tatterson, [Email address]  
**Program:** Break Through Tech AI Studio - Fall 2026

---

## 🏢 About KPMG

KPMG is a global leader in audit, tax, and advisory services, providing insights and expertise to a diverse clientele across various industries. Our commitment to innovation drives us to integrate technology into our solutions, enhancing business performance and fostering success.

---

## 🎯 The Challenge

### Project Summary
In this project, you will use publicly available AI research data (e.g., arXiv papers and metadata) and retrieval-augmented generation (RAG) techniques with large language models to build an agent that retrieves relevant research, summarizes key findings, and translates them into business-relevant insights. This will help our organization address the challenge of efficiently monitoring and operationalizing the rapidly growing volume of AI research. Abhinav Raghunathan will serve as the KPMG business owner / Challenge Advisor for the project, responsible for guiding business relevance, success criteria, and stakeholder feedback.

### Success Criteria
Success will be measured based on: Retrieval relevance: Ability to return appropriate research papers for a given query; Summary quality: Accuracy and clarity of synthesized research insights; Business usefulness: Extent to which outputs translate technical content into actionable business implications; Human evaluation: Validation by KPMG stakeholders reviewing relevance and accuracy of outputs; Human-in-the-loop checkpoint: KPMG stakeholders will review retrieved sources, summaries, and business implications before outputs are used for internal decision-making, thought leadership, or client-facing discussions. A successful outcome will be: A working prototype that enables natural-language querying of AI research and produces summarized, business-relevant outputs with citations; Documented evaluation approach and results; Demonstrated applicability for internal enablement and client conversations; A final solution package that includes prototype documentation, evaluation results, scope limitations, and a final presentation suitable for stakeholder review.

### Project Milestones

Use these milestones to guide your work. Your team will create a **GitHub Projects board** to track tasks within each milestone.

| Month     | Milestone                  | Key Activities                                                              |
|-----------|----------------------------|---------------------------------------------------------------------------|
| **September** | Data Exploration         | Explore dataset, define evaluation framework, benchmark queries, develop baseline retrieval pipeline (RAG setup) |
| **October**   | Implement Retrieval + Summarization | Implement retrieval + summarization pipeline, develop prompt engineering approach for business translation, begin evaluation (relevance and accuracy testing) |
| **November**  | Model Refinement         | Refine model outputs and improve ranking/relevance, build user interface, document solution and prepare final presentation |
| **December**  | Final Deliverables       | A working prototype, documented evaluation, demonstrated applicability, and final solution package |

> **Note for the team:** Please create a GitHub Projects board in this repository to break these milestones into weekly tasks. Go to the **Projects** tab → **New project** → Choose **Board** → Add columns for each month.

---

## 📊 Dataset

**Name and Source:** Publicly available AI research data from [arXiv](https://arxiv.org/)  
**Format:** Categorical and Text, primarily in PDF format  
**Size:** under 1gb  
**Location:** [Link to dataset or instructions for accessing it]

### Key Details
- Publicly available AI research data (e.g., arXiv papers and metadata) from https://arxiv.org/. The data is Categorical and Text, primarily in PDF format. Partial documentation exists, and it will require some cleaning/preprocessing.
- [Any known limitations or preprocessing needed]
- [Link to data dictionary or documentation, if available]

---

## 🛠️ Suggested Approach

**ML Problem Type:** NLP / Retrieval-augmented Generation

**Recommended Libraries:**
- Retrieval-augmented generation (RAG) techniques
- large language models (LLMs)
- Natural Language Processing (NLP)
- Generative Models
- Transfer Learning / Pre-trained Models

**Evaluation Metrics:**
- Retrieval relevance
- Summary quality
- Business usefulness
- Human evaluation
- Business impact assessment

---

## 📚 Resources to Get Started

The following resources will help your team understand the problem space and potential technical approaches for this project:

**Background Reading:**
- [Introduction to Retrieval-Augmented Generation](https://example-link.com)
- [The Growing Importance of AI Research in Business](https://example-link.com)

**Technical Tutorials:**
- [Getting Started with NLP](https://example-link.com)
- [Guide to RAG Techniques](https://example-link.com)

**Code Examples:**
- [GitHub: RAG Example Repo](https://github.com/example/repo)
- [Sample Implementation of NLP Techniques](https://example-link.com)

**Other:**
- [Papers on RAG and NLP Models](https://example-link.com)

*Feel free to explore beyond these, and share anything interesting you find with me!*

---

## 🤝 How We'll Work Together

**Check-ins:** During our biweekly 60-min AI Studio Lab Section meeting block (2nd and 4th week of every month)  
**Communication:** Slack (Break Through Tech workspace) or email  
**Response time:** Within 48 hours on weekdays  

**Recommended Tools:**
- **Coding:** Google Colab, VS Code
- **Collaboration:** GitHub, Notion
- **Virtual Meetings:** Zoom, Google Meet

---

## 🚀 Getting Started

1. **Review this overview document** and note any questions for our first meeting
2. **Begin reviewing the dataset** using the link above
3. **Read the GitHub Projects documentation** [here](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)

I'm excited to work with you!

---

## ❓ Questions?

Please bring any questions to our first meeting during the week of August 24th (Break Through Tech's Bridge to Studio - Session B).
