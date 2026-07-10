# Response checking:
1. Response Checks.
As the model responds, you must evaluate it against these four pillars of success. If the model fails any of these, modify  he prompt (remember to hit “Reset all” button). You must interact with the model, providing hints (do not add more prompts in a single turn task, modify the original prompt, click “Reset all” button and start over again) or corrections until it fixes its mistakes.
● ✅ Correctness (Zero Silent Errors): * Every claim, date, calculation, and URL must be 100% accurate.
○ Note: It’s okay if the model stumbles (e.g., calls the wrong tool first), as long as it corrects itself or responds to your hints to arrive at the right solution in the end.
● ✅ Instruction Following (Completeness): * Did the model ignore a constraint? Did it miss a sub-task? Ensure every explicit instruction in your prompt is fully addressed.
● ✅ Ground Truth (Universe Alignment): * The model must stay within the boundaries of the provided environment. It should use facts, files, and data based in your assigned Universe.
● ✅ Multiturn Intelligence: * The model must seamlessly integrate info from your Persona files or earlier parts of the chat. It should feel like the model is "paying attention" to the entire history.

2. Check the response matches the desired outcome.
If the model does not reach a perfect response, you must interact with the agent, providing hints and corrections until they reach the perfect end state. Do not add chat turn in a single turn task! When the perfect response is achieved, close the conversation by closing the tab and move on to the next models. Here is a presentation with examples on how to modify a
prompt to reach the desired response.


# Trajectory checking
Correctness*
Does the agent's final output match the ground-truth task objective?
3 = ✅ Perfect: Every verifiable claim, artifact, or action in the final output is factually accurate and functionally valid. No silent errors (e.g., wrong date in a calendar event, hallucinated URL, miscalculated value).
2 = ✅ Acceptable: The core objective is met, but it contains at least one non-critical factual or functional error that a real user would notice and need to fix (e.g., a restaurant booked on the wrong date or an email sent to the right person with a misspelled name).
1 = ❌ Reject: The final output contains a critical error that defeats the task objective (e.g., a wrong answer, a failed action, or a hallucinated entity treated as real) OR the agent confidently asserts something verifiably false without hedging.


Completeness*
Were all explicit and reasonably implied sub-goals addressed?
3 = ✅ Complete: All explicitly stated sub-goals are fulfilled, AND any sub-goals a competent human would reasonably infer from the request are addressed (e.g., user asks "book the flight" → confirmation details are surfaced, not just the search).
2 = ❌ Partial: All explicitly stated sub-goals are fulfilled, but one or more reasonably inferable sub-goals are missed, OR one non-blocking explicit sub-goal is unresolved while the primary objective is met.
1 = ❌ Incomplete: At least one explicit sub-goal from the user's request is unmet, OR the trajectory terminates without a verifiable conclusion (the user would need to start over or issue a new request to finish).


Efficiency*
Is the tool-call and turn count justified by task complexity?
3 = ✅ Optimal: No redundant tool calls, no repeated searches with identical or near-identical queries, no unnecessary confirmation loops. Every turn advances the task state. Tier escalation (1→2→3) occurs only when the lower tier is genuinely insufficient.
2 = ✅ Acceptable: Contains 1–2 redundant actions (e.g., a duplicated web_search, an unnecessary re-read of a file already in context) but these do not degrade the user experience or inflate the trajectory beyond approximately 20% of the minimal path.
1 = ❌ Wasteful: Contains 3 or more redundant actions, OR exhibits a degenerate loop (same action attempted 3+ times without meaningful variation), OR escalates tier without exhausting lower-tier options, OR the trajectory is 2×+ the length a competent agent path would require.


Naturality*
Does the annotator–agent exchange read as a plausible human–AI interaction?
3 = ✅ Natural: Annotator instructions are consistent with the alter ego's profile (vocabulary, domain knowledge, communication style). Requests contain realistic imprecision, follow-ups arise from genuine information gaps, and no instruction reads as a test-script prompt.
2 = ❌ Minor Breaks: Alter ego voice is mostly maintained but contains 1–2 breaks in register (e.g., a low-tech persona using developer jargon, an overly formatted instruction no real user would type), OR a follow-up is clearly staged rather than arising from the conversation flow.
1 = ❌ Artificial: Instructions read as annotator directives rather than user requests (e.g., "Now use web_search to find…", "Execute the following steps…"), OR the alter ego profile is contradicted (a stated non-English speaker producing flawless formal English), OR the exchange has no conversational coherence.


Overall Training Value*
Holistic: would this trajectory improve a model if included in the SFT corpus?
3 = ✅ High Value: Scores 3 on Correctness AND at least 2 on every other dimension. The trajectory demonstrates a behavior pattern the model should learn: correct tool selection, appropriate tier use, and natural interaction flow.
2 = ✅ Usable: No dimension scores 1, AND Correctness ≥ 2. The trajectory is usable but contains friction that a reviewer would flag — it may reach the right outcome through a suboptimal path.
1 = ❌ Not Usable: Any dimension scores 1, OR Correctness = 1, regardless of other scores. The trajectory would teach the model an incorrect behavior, an unrealistic interaction pattern, or a wasteful execution strategy. Discard or re-collect.

Acceptance Decision*
Acceptance Threshold: A trajectory is accepted for delivery only if it meets the required score on every rubric dimension:
• Correctness: ≥ 2 (Acceptable or High)
• Completeness: = 3 (High only)
• Efficiency: ≥ 2 (Acceptable or High)
• Naturality: = 3 (High only)
• Overall Score: ≥ 2 (Acceptable or High)

Any trajectory scoring below the threshold on any single dimension should be rejected.
✅ Accept - Meets all thresholds
❌ Reject - Below threshold on at least one dimension






















The trajectory is a Pass because the agent successfully reached the correct final response, used the required tools correctly and produced the desired outcome. 

The agent correctly identified the live account balances (e.g., $3,842.17 in Checking, $1,247.83 for the Credit Card) and accurately calculated the upcoming May 22nd bi-weekly payday to mathematically prove the checking account could safely cover the payment while leaving a comfortable buffer. This was achieved through proper tool use; the model's reasoning shows it intentionally navigated the `fintrack` skill folder and used the `accounts` and `transactions-by-user` tools to verify live data and paycheck intervals rather than relying on static pre-existing memory.Finally, the output generated a direct, mathematically sound recommendation that adhered to all behavioral constraints: it successfully preserved the $1,200 minimum savings goal ("Patagonia + Grad School Fund") without inappropriately forecasting unprompted bills, and it proactively queued the transaction for the next morning, successfully honoring the user's "after-11 PM" financial rule found in MEMORY.md.