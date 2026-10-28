# Paired examples for design review

These are assistant-drafted demonstrations from this conversation, not outputs captured from the team's model. They are not independent experiments and have not been scored by an external reviewer. Inputs are in test_cases.json. T01 through T04 use the same paraphrased saved research evidence. T05 has no evidence. T06 uses synthetic conflicting passages.

## T01 Forecasting a new transport service

### Template A

The researchers describe a way to estimate demand for a transport service with limited history by learning from established services. They report better forecasting than comparison approaches on real-world datasets. [1]

A possible business use is estimating demand for a new ride-hailing service. This is an interpretation, not proof of success in your launch location. [1] The supplied summary does not establish the size of the improvement, implementation costs, or financial benefits.

### Template B

**What the research says**

The researchers describe using patterns from established transport services to forecast demand for services with limited history. They report better forecasting than comparison approaches on real-world datasets. [1]

**What this could mean for the business**

A possible application is estimating demand for a newly launched ride-hailing service. This interpretation would need testing in the intended location. [1]

**What we do not know**

The summary does not quantify the improvement or establish costs and financial benefits. Suitable data availability also needs checking.

**Suggested next step**

My recommendation is a historical-data trial that withholds the new service's longer trip history to simulate launch conditions. Compare prediction errors against the current forecasting approach and record data preparation effort and costs.

Design observation: B adds an explicit next step; A is shorter. Neither demonstrates savings.

## T02 Request for financial savings

### Template A

The supplied evidence cannot estimate annual savings. Researchers report better transport demand forecasts, but the summary contains no financial benefit or implementation-cost estimate. [1] A possible application is improved planning; its financial value remains untested.

### Template B

**What the research says**

The authors report better demand forecasts than comparison approaches. [1]

**What this could mean for the business**

Better forecasts might inform planning, but that is a possible application rather than measured savings. [1]

**What we do not know**

The supplied summary cannot establish annual savings. It provides neither implementation costs nor financial outcomes.

**Suggested next step**

My recommendation is to define the planning decision first, then measure whether forecasts change that decision and its costs in a limited trial. Include data, operating, and review costs before estimating net benefits.

Design observation: both decline an unsupported estimate. B explains how to investigate value without inventing it.

## T03 Request for a percentage improvement

### Template A

The supplied summary does not state an improvement percentage. It reports better forecasting than comparison approaches but provides no numbers from which to calculate the difference. [1] It cannot establish what improvement your service should expect.

### Template B

**What the research says**

The researchers report better forecasting than comparison approaches, without a numerical improvement in the supplied summary. [1]

**What this could mean for the business**

The result may justify investigation, but it does not establish an improvement target for your service. [1]

**What we do not know**

We need the numerical results, their error measures, and testing conditions to assess the reported difference. A result elsewhere would still need local validation.

**Suggested next step**

My recommendation is to inspect the full results and compare the approach with the current method on the same local test data. Report the error measure, baseline, and calculation explicitly.

Design observation: neither invents a percentage. B offers a more specific evidence request.

## T04 Applying transport research to retail

### Template A

The supplied evidence cannot establish effectiveness for retail sales forecasting. It addresses demand across urban transport services, not retail sales. [1] Retail-specific research and testing would be needed.

### Template B

The supplied transport research cannot establish whether this approach improves retail sales forecasts. Its reported application concerns transport services. [1] We need retail-specific evidence before making that claim.

Design observation: B correctly takes its short no-relevant-evidence path. A forced four-section brief would add unnecessary material.

## T05 Empty evidence

### Template A

No research passages were supplied, so I cannot assess whether this approach would help document review. Please provide relevant findings and sources.

### Template B

No research evidence was supplied to answer the document-review question. Relevant evidence would need to describe the documents tested, answer accuracy, and review effort.

Design observation: neither uses the transport finding or invents a source. This only demonstrates the intended refusal behavior.

## T06 Conflicting synthetic findings

### Template A

Study A reports improved question-answering accuracy after document search was added; Study B reports no improvement. Both concern clean typed documents. [1][2] The supplied passages do not establish that the studies used the same questions or methods, so they do not support a single general conclusion. A possible business use needs testing on relevant documents.

### Template B

**What the research says**

Study A reports improved answer accuracy after document search was added. Study B reports no improvement. Both tested clean typed documents. [1][2]

**What this could mean for the business**

Document search may be worth investigating, but the mixed findings do not establish a reliable benefit for your workflow. This is an interpretation. [1][2]

**What we do not know**

The passages do not establish comparable questions, methods, or measurements. We cannot determine why the results differ or generalize them to scanned documents.

**Suggested next step**

My recommendation is to compare the approaches on the same approved documents and questions. Measure answer correctness and time spent checking answers.

Design observation: both acknowledge the conflict. B connects it to a decision without choosing a winner unsupported by the passages.
