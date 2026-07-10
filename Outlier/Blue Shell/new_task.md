🛡️OpenClaw Multimodal - Rubrics🛡️
🏗️ Project Overview

In this project, you will engage with one AI model using the OpenClaw interface. You will have to create a prompt and provide multimodal inputs to the model to help us evaluate its performance using your conversation history.

What qualifies as a multimodal task?

A task should be counted as multimodal only if visual, audio, or media evidence is necessary to complete at least one core requirement. Attaching an image to a task that can be solved from text alone does not count.

Strong multimodal tasks require the agent to inspect, compare, extract from, or generate visual/media artifacts as part of the task outcome

Multimodal requirements

Real-world inputs: Use messy, realistic files — IMG_0427.HEIC, duplicates, blurry shots, skewed PDFs, mixed orientations. No curated-JPG-only sets.

Diversity: Various scenarios. Don't recycle the same prompts.

Cross-modal reasoning: ≥50% of tasks should fuse ≥2 modalities (e.g., PDF lease ↔ walkthrough video). Prefer multi-skill/multi-app tasks.

Format realism: Mix HEIC/JPG/PNG/WEBP and varied dimensions — not all 1024×1024 PNGs.

Multi-artifact consistency: When generating multiple artifacts, rubrics should cross-check them against each other.

Depth: Favor longer reasoning chains (e.g., identify issues → cross-reference source → produce report) over shallow input→output tasks.

Rubrics: Check actual content and values, not just artifact existence.

NEW 5/15 🌐 Environment App

In the next step, you will find the Universe Explorer app.

This is the task-specific environment. It shows the exact skills, tables, and accessible tools for this particular task — i.e., what the model can actually use in that session. The expectation is that the prompt should be solvable using only what appears in Universe Explorer for this task.

Add these IDs to the Universe Explorer app so it pulls the information of the universe assigned to this task.

Category	Assigned Value
Environment ID	openclaw-lucia_gutierrez-multi-8o2gzp9r
Service Universe Artifact ID	openclaw-lucia_gutierrez-universe-jl36qt2t
📋 Your Task Parameters (required)

Please ensure your prompts align strictly with the following assigned specs:

Category	Assigned Value
Task Type	Single-turn
Category	Visual Learning
Category Description	Student, parent, or self-learner uses academic media (worksheets, lecture slides, lab photos, textbook pages) to understand or document content. Agent OCRs handwriting, interprets diagrams, and produces study artifacts (notes, lab reports, solution sets, study guides).
Subcategory	Lab/Fieldwork Documentation
Universe	lucia_gutierrez
Multimodal input strong suggestion	upload image
🚀 High-Level Task Workflow

Realistic, grounded, and verifiable tasks lead to the strongest trajectories.

🧠 Step 0 → Draft a realistic prompt aligned with the Universe, Category, and Subcategory. Interact with the universe first to make it grounded.
📖 Step 1 → Create the story draft: Agent Objective, Desired Outcome, Category and Subcategory, and the Multimodal Input (Zip Folder).
✍️ Step 2 → Add the final prompt version, fully aligned with the story draft, and send it to the OpenClaw agent.

For the OpenClaw Environment to work, make sure to do this:

Upload your files as a .zip file in the workspace: Click on 'Upload Files' in the top right corner of the environment.
Open the Dedicated OpenClaw Tab: Before you begin, make sure the environment is fully loaded and working.
Input Your Prompts: Follow the normal trajectory — run your prompts through the chat on the webpage.
Run the Gatherer: Only after finishing the trajectory, press the Next button beneath the OpenClaw cards. This will retrieve the trajectory and allow you to complete the rest of the task.
🔎 Step 3 → Spot agent mistakes in the initial trajectory. At least 50% of the total rubric score must fail.
📋 Step 4 → Generate the rubrics and mark each one as Present or Not Present (against the initial agent's trajectory).
🧾 Step 5 → Justify all "Not Present" positive and "Present" negative rubrics.
NEW 5/29 Artifacts Library 📦

Please use this Artifacts Library to source files for your task.

Usage:

Click an item to preview it.
Click "Claim this" to download it.

Important Rules:

DO NOT claim an artifact until you are sure you will use it.
Each artifact can only be used once across the team; once claimed, it will disappear from the library.
You may combine these with external files, provided they comply with our legal regulations.

Support: If you have questions or hit download issues, please reach out to the project team in the Outlier Community or the War Room.

Questions ❓

If you run into any issues or have questions about the annotation process, reach out to your QM on our Outlier Community channel or join our War Room.

