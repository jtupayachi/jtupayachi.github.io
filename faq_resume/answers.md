FAQ Resume - Answers


Project: RECOIL - Cognitive Freight Transportation Digital Twin
@ Lead AI/Data Engineer | DOE ARPA-E DE-AR0001780 ($3M) | Jul 2024 - Mar 2026


Q: What was the real-world or simulated scale of the intermodal system modeled?

Modeled a national U.S. freight network spanning 100+ intermodal nodes across road, rail, waterway, and EV charging infrastructure; the digital twin simulates multi-modal route decisions at network scale, validated against DOE ARPA-E simulation benchmarks (arXiv:2410.18089).


Q: What were the measurable improvements achieved in cost/CO2 reduction?

The intermodal routing optimizer I designed integrates road, rail, and waterway modes using ontology-guided GIS-based optimization; it projects a 15-20% reduction in per-route CO2 emissions compared to single-mode truck-only baselines by shifting freight to lower-emission rail and waterway legs, validated through DOE ARPA-E simulation benchmarks (arXiv:2410.18089).

The TW-GCN (Traffic-Weather Graph Convolutional Network) I built and published for EV charging demand forecasting - trained on real proprietary ChargePoint data across 86 stations over 13 months in Tennessee - achieved MAE of 0.064 and RMSE of 0.573, which is more than 10x lower MAE than all classical baselines tested: SVM (0.649), XGBoost (0.941), Random Forest (0.936), LightGBM (0.948), Linear Regression (1.022). Accurate demand forecasting feeds directly into the routing optimizer to reduce idle charging cost and grid stress per shipment leg (arXiv:2510.09048).

A real-time streaming feedback loop using simulated sensor data continuously re-optimizes intermodal routing under dynamic weather, traffic, and demand conditions; this closed-loop architecture reduces unnecessary truck miles and associated fuel cost per shipment compared to static batch-optimized baselines.

The U.S. transportation sector accounted for 28% of total U.S. GHG emissions in 2022 (EPA), with medium- and heavy-duty trucks contributing 23% of transport-sector emissions. RECOIL directly targets this segment, making a 15% route-level CO2 reduction meaningful at national freight scale.


Q: What specific metrics or user feedback validated the success of the trade-off analysis chatbot?

The production chatbot was used by 20+ domain experts, researchers, and DOE ARPA-E program stakeholders during simulation demonstration phases; users independently ran cost-time-CO2 what-if queries ("What is the emissions impact of shifting 40% of this corridor's load to rail?") with no engineering support required.

Qualitative feedback from DOE sponsor presentations confirmed that non-technical decision-makers could interpret and act on trade-off outputs in scenarios where previously an engineer needed to be present to translate model results, reducing decision turnaround from hours to minutes.

The chatbot is deployed to production at m1.recoil.ise.utk.edu, backed by a knowledge graph (Neo4j + vector embeddings) and a BERT/sentence transformer domain literature index, surfacing both quantitative optimization results and relevant research findings in a single natural-language response.

Formal user-study metrics are being finalized for the platform evaluation paper submitted to Computers & Industrial Engineering (ID: CAIE-D-25-05889, Xu, Sun, Tupayachi, Omitaomu et al.).


Project: Oak Ridge National Laboratory - Materials & Scientific AI
@ Research Fellow | DOE FES Fusion Materials Sciences + DOE EM/NSRD | Mar 2025 - Present


Q: What was the scale of data processed, or how much did your solution improve the speed/accuracy of scientific discovery?

Analyzed 1,000+ SEM images through a ViT-based multi-pathway agentic pipeline (microstructure analysis, defect detection, phase identification), replacing days-per-batch manual expert annotation with automated, reproducible classification and structured scientific reporting; ingested and cross-referenced 200+ lithium breeder blanket research papers via a LangChain + LangGraph RAG pipeline (Qwen/Llama via Ollama, vector DB), cutting expert literature review cycles from 2–5 days to under 1 hour per batch with full source traceability.


Project: Indra - Enterprise Data Engineering
@ Data Engineer | Mar 2022 - Aug 2022


Q: What was the approximate size of the data migration, and what specific performance gains did Spark tuning achieve?

I migrated 3 core enterprise tables, each with approximately 5,000 variables (columns), covering a client portfolio of approximately 18 million customers from a legacy Oracle data warehouse to a partitioned cloud lakehouse on AWS (S3 + EMR + Hive). Each table was a full transformation step, not a copy: it required schema redesign from normalized Oracle structures to dimensional star-schema models, entity resolution and deduplication to reconcile 18M client records duplicated across systems, and full business logic re-implementation in PySpark/Scala to replace Oracle stored procedures.

Spark executor memory and core allocation were calibrated per-job to prevent OOM shuffle spills on 5,000-column wide table joins at 18M-row scale; broadcast join thresholds were raised to eliminate shuffle-heavy sort-merge joins on dimension tables; partition pruning and dynamic partition overwrite reduced I/O by scanning only relevant date-range partitions; coalesce and repartition strategies eliminated the small-file problem degrading downstream query performance in the lakehouse.

Average ETL job execution time dropped from 3-4 hours to under 40-45 minutes [confirm exact times from project records], unblocking the downstream data science team to run full model training and analytics iterations within a working day rather than waiting overnight.

The resulting lakehouse became the primary data source for customer analytics, model training, and KPI reporting across all 18 million clients; all pipeline changes were deployed through Jenkins CI/CD with automated unit tests, live deployment, rollback, and backup - zero data loss during the migration window.


TA Roles - IE406/408 (Simulation) & IE483 (Reliability Engineering)
@ University of Tennessee, Knoxville | Jan-May 2022 & Aug-Dec 2022


Q: Describe a specific advanced concept or tool you taught or led a workshop on.

IE406/408 Simulation: Led a hands-on AnyLogic lab for ~25 students connecting discrete-event simulation to deep reinforcement learning — students built a wildfire suppression MDP (state: fire perimeter + resource positions; action: unit dispatch; reward: suppression outcome minus cost), trained a policy gradient agent, and benchmarked it against 2 baseline heuristics (nearest-unit, priority-queue dispatch) on suppression time, resource utilization, and cost per incident; based directly on my own ANNSIM 2024 publication.

IE483 Reliability Engineering: Designed and led a Weibull analysis + FMEA workshop where students applied MLE to fit exponential, Weibull, and lognormal distributions to real industrial sensor failure datasets, estimated Remaining Useful Life (RUL) under varying operating conditions, and computed Risk Priority Numbers (RPNs) through structured FMEA sessions — directly connecting statistical theory to predictive maintenance practice.


Project: Globokas - Business Intelligence Analyst
@ BI Analyst | Globokas | Jan 2022 - Mar 2022


Q: What was the scope of the data integration built for the BI platform?

Integrated 10+ heterogeneous sources — transactional databases, collections systems, billing platforms, and cash-pickup payment center feeds — into unified BigQuery + Looker Studio / Power BI analytics pipelines, delivering executive dashboards and KPI reporting for internal business stakeholders across operational and financial decision workflows.


Project: Enel Distribución - Data Analyst
@ Data Analyst | Enel Distribución | Nov 2020 - Dec 2021


Q: What was the quantifiable impact of the unsupervised learning segmentation on targeted campaign performance?

Segmented 1.6M utility customers into behavioral K-means clusters to prioritize payment recovery campaigns; targeted outreach to high-propensity-to-default segments improved collection campaign hit rate by ~15% over untargeted baselines, reducing cost-per-recovered-account by directing call-center and field resources exclusively to the highest-yield customer groups.


Project: ACTAPP - Active Caregiver's Toolkit
@ Mobile Developer | Hillman Emergent Innovation (HEI) | Jul 2024 - Present


Q: What specific data did the chatbot track, and did it lead to measurable changes in user behavior or caregiving efficiency?

I instrumented the integrated ChatBot to capture FAQ interaction logs (every question posed, categorized by topic: exercise guidance, scheduling, motivation, health information), page visit sequences and navigation paths before and after chatbot interactions, session durations, return frequency between sessions, and feature engagement metrics for each intervention prompt, activity tracker, and reminder feature triggered per session.

Pre/post chatbot behavior tracking recorded whether users who interacted with the chatbot subsequently completed a scheduled physical activity entry versus those who did not; early analysis showed caregivers who engaged with the chatbot had measurably higher session completion rates and more consistent return patterns [confirm % from HEI preliminary data].

Interaction logs identified the top 3 most-accessed informational topics - exercise modification for caregiver fatigue, scheduling around care duties, and motivation during high-stress caregiving periods - which the research team used to restructure intervention content prioritization in the next app update cycle.

The tracking data feeds directly into the formal behavioral outcome analysis for the HEI study and contributes to the manuscript submitted to npj Digital Medicine (CliniSense AI for Automated Clinical Skills Assessment with Real-Time Feedback); all behavioral data is anonymized at collection and stored under IRB protocols - no PII retained in interaction logs.

