# The Agentic Security Manifesto

## Same primitives. New controller. Revised risk model.

**By Ryan Sevey**  
**Version:** 1.1 public draft

---

We are not arguing that agentic AI invents every underlying security primitive.

It does not.

HTTP is still HTTP.  
`curl` is still `curl`.  
IAM is still IAM.  
APIs are still APIs.  
MFA is still MFA.  
EDR is still EDR.  
DLP is still DLP.  
Segmentation is still segmentation.  
Injection is still injection.  
Confused deputy is still confused deputy.  
Automation is still automation.  
Excessive permissions are still excessive permissions.  
Data classification is still data classification.  
Logging is still logging.  
AppSec is still AppSec.  
Cloud security is still cloud security.

But primitives are not the whole risk model.

The security meaning of a primitive changes when it is selected, sequenced, retried, and adapted by a **goal-directed, non-deterministic, tool-using, memory-bearing, feedback-sensitive controller**.

Agentic AI does not merely make old actions faster. It changes:

```text
who decides the next action
which goal drives the action
how failure is interpreted
which tool is selected
how internal authority is used
how data boundaries are crossed
how systems are chained
how long the objective is pursued
how much telemetry is generated
how quickly defenders must contain the sequence
how hard it is to reconstruct intent
```

The primitive is old.  
The controller is new.  
The risk model changes.

The mature position is not:

```text
Everything is new.
```

The mature position is:

```text
Existing controls govern the probabilistic action graph.
Agentic security governs the goal-directed controller searching that graph.
```

---

## 1. The thesis

Agentic AI security is different because agents do not merely execute instructions.

They pursue objectives.

A traditional script follows a fixed path:

```text
Goal → Script → Tool call → Error → Stop
```

An agentic system follows a feedback loop:

```text
Goal → Plan → Tool use → Observation → Memory → Retry → Adapt → Continue
```

The critical difference is not speed.

The critical difference is that:

> **Failure becomes feedback.**

A static automation receives `403 Forbidden` and stops.

An agent receives `403 Forbidden`, interprets the denial, updates state, searches for another path, selects another tool, and continues pursuing the same objective.

That is the control-loop shift.

That is why the guided missile analogy works.

A cannonball and a guided missile are both delivery systems. But a guided missile senses, corrects, and continues toward a target. The important difference is not “more force.” The important difference is **closed-loop objective pursuit**.

Agentic AI introduces that kind of shift into software systems.

---

## 2. The opposing view, fairly stated

The opposing view deserves to be taken seriously.

It says:

> Agentic AI does not create a fundamentally new security problem. The underlying actions are still familiar: API calls, credentials, automation, web requests, injection, data access, excessive permissions, logging gaps, and confused-deputy problems. Security teams already know how to handle these things through least privilege, defense in depth, audit logging, DLP, segmentation, secure SDLC, monitoring, and incident response.

This view is partially correct.

It is correct at the **primitive layer**.

Agentic AI does not make an API call metaphysically new. It does not make OAuth new. It does not make authorization new. It does not make data classification new. It does not make logging new.

It is also correct that defenders can automate too. The agentic race is not automatically offense-favored. If attackers use machine-speed exploration but defenders remain human-speed, the attacker gains advantage. If defenders build machine-speed visibility, governance, and containment, the race changes.

But the opposing view is incomplete when it stops at the primitive layer.

The right question is not:

```text
Are the low-level primitives new?
```

The right question is:

```text
Do old primitives behave differently when controlled by an autonomous,
goal-seeking system with tools, memory, feedback, and delegated authority?
```

Our answer is yes.

The mature position is not:

```text
Everything is new.
```

The mature position is:

```text
The primitives are familiar, but the operating model has changed.
```

And when the operating model changes, the risk model changes.

---

## 3. The disagreement is about abstraction layer

Most “this is not new” arguments operate at the wrong layer.

They say:

```text
The request is still just an HTTP request.
```

We say:

```text
The request may be familiar. The controller choosing the request is not.
```

They say:

```text
This is still just automation.
```

We say:

```text
Traditional automation executes predefined steps. Agentic AI searches for a path to satisfy a goal.
```

They say:

```text
A human attacker could do this too.
```

We say:

```text
Yes. But traditional security often relies on the human being bounded by time, attention, expertise, cost, and manual iteration speed.
```

They say:

```text
The same controls still apply.
```

We say:

```text
The same control families remain necessary. But they must now constrain both the reachable graph and the goal-directed controller searching it.
```

The cleanest summary is:

> **Same primitives. New controller. Revised risk model.**

---

## 4. The model is a reasoning scaffold, not predictive actuarial math

The equations in this manifesto are not intended to produce precise numeric risk scores.

They are a reasoning scaffold.

They clarify:

```text
where existing controls still apply
where agentic behavior changes the race
where conventional cyber becomes a cadence problem
where AI-native control-surface risk appears
where defender automation matters
where governance must constrain the loop
```

Do not plug guesses into these equations and present the output as a forecast.

Using the model quantitatively would require:

```text
empirical calibration
real telemetry
rate estimation
distributional assumptions
parameter fitting
validation against observed incidents
```

The model is useful because it prevents two bad conclusions:

```text
Everything is new.
Nothing is new.
```

The reality is:

```text
Existing controls govern the graph.
Agentic security governs the controller.
```

---

## 5. The enterprise is a constrained, probabilistic action graph

Model the enterprise as an action graph:

```text
G = (V, E)
```

Where:

```text
V = systems, identities, tools, data stores, workflows, users, agents
E = possible actions or transitions between them
```

Security controls shape the graph:

```text
IAM
MFA
network segmentation
rate limits
hardware roots of trust
tool authorization
data policy
approval gates
logging
containment controls
```

But controls do not simply remove edges perfectly.

In real environments, edges have residual reachability, cost, and risk.

So the controlled graph is:

```text
G_C = (V, E, w_e)
```

Where each edge has weights such as:

```text
p_reachable(e)
cost_time(e)
cost_telemetry(e)
cost_privilege(e)
data_sensitivity(e)
approval_required(e)
containment_difficulty(e)
```

This matters because enterprise controls are imperfect.

An edge may be blocked in theory but reachable through:

```text
misconfiguration
over-permissioning
stale session state
workflow exception
delegated tool authority
weak data policy
business-context-dependent access
```

So the right statement is:

> **Controls do not merely remove edges. They change edge probabilities, costs, and detection surfaces.**

This is why agentic systems matter. An agent cannot magically bypass a hard boundary. But it can search for residual paths that remain reachable because of configuration drift, delegated authority, weak workflow design, excessive permissions, or business-context-dependent exceptions.

---

## 6. The actor is a goal-directed controller

A static script, a human, an agent, and a defensive automation system can all operate inside the same graph.

The difference is the controller policy:

```text
π_i(a_t | h_t, G_C, g_i)
```

Where:

```text
π_i = controller policy for actor i
a_t = action selected at time t
h_t = history so far
G_C = controlled enterprise action graph
g_i = actor objective or goal
```

A static script usually follows a fixed path:

```text
Goal → predefined step → predefined step → error → stop
```

A human attacker is adaptive but bounded by:

```text
time
attention
expertise
fatigue
cost
manual iteration speed
available context
```

An agentic executor is:

```text
goal-directed
tool-using
stateful
feedback-sensitive
potentially parallel
bounded by controls, telemetry, policy, and tool reach
```

So the agentic delta is not that the primitive changed.

It is that the controller changed.

```text
curl is still curl.
The difference is π(a_t | h_t, G_C, g): who or what chooses the next curl.
```

This is why “same attacks, faster” is incomplete.

A script asks:

```text
Can I run this step?
```

An agent asks:

```text
How else can I accomplish the goal?
```

That “how else” is the new security problem.

---

## 7. Risk is a hitting-time race

Define:

```text
τ_impact = time until material impact
τ_G = time until preventive governance blocks the action chain
τ_D = time until detection
τ_K = time to contain after detection
τ_stop = time until hard controls, exhaustion, approval gates, or policy limits stop the actor
```

Detection alone is not containment:

```text
τ_detect+contain = τ_D + τ_K
```

The bad event is:

```text
𝔈 = { τ_impact < min(τ_G, τ_D + τ_K, τ_stop) }
```

Risk is:

```text
Risk = E[Impact | 𝔈] × P(𝔈)
```

This is stronger than saying:

```text
Risk = probability × scalar impact
```

because impact is a distribution.

The defender’s dilemma appears when we consider multiple paths.

For each path:

```text
𝔈_p = impact occurs through path p before governance, containment, or stop
```

Across all reachable paths:

```text
𝔈 = ⋃_{p ∈ Paths(G_C, g)} 𝔈_p
```

So:

```text
P(𝔈) = P( ⋃_{p ∈ Paths(G_C, g)} 𝔈_p )
```

If paths were independent, an approximation would be:

```text
P(𝔈) ≈ 1 - ∏_{p}(1 - P(𝔈_p))
```

But paths are usually correlated because they share identities, tools, data stores, policies, workflows, and telemetry.

The key operational point is:

> **Attackers need one viable path. Defenders need enough governance, visibility, and containment across the reachable path space.**

---

## 8. Effective action rate is capped, and the caps are dynamic

Agentic systems do not get infinite speed.

Effective action rate is capped by chokepoints:

```text
r_eff(P, t) =
min(
  P × r_lane(t),
  r_tool(t),
  r_auth(t),
  r_rate(t),
  r_compute(t),
  r_approval(t),
  r_network(t)
)
```

Where:

```text
P = parallel attempts or agents
r_lane = per-lane action rate
r_tool = tool/API throughput ceiling
r_auth = authentication/session ceiling
r_rate = rate-limit ceiling
r_compute = compute ceiling
r_approval = approval/workflow ceiling
r_network = network/infrastructure ceiling
```

But these ceilings are not fixed.

Attackers may try to relax the binding constraint:

```text
steal more credentials
find another API route
compromise an approver
move to another environment
use lower-rate paths
```

Defenders may tighten the constraint:

```text
revoke sessions
disable connectors
require approvals
rate-limit tools
segment networks
reduce token scope
```

So the ceilings are part of a dynamic game:

```text
r_j(t+1) = r_j(t) + Δ_offense_j(t) - Δ_defense_j(t)
```

Plainly:

> **Effective agent speed is capped by chokepoints, but both attacker and defender can act on the chokepoints.**

---

## 9. Parallelism buys exploration and sells stealth

Parallelism is not a free multiplier.

More agents or attempts may improve search coverage, but they also generate more telemetry.

Detection evidence is nonlinear.

There is usually:

```text
a noise floor
a gray zone
a threshold
a saturation point
```

A more realistic detection-evidence model is:

```text
z_t = β_0
    + β_1 log(1 + event_volume_t)
    + β_2 anomaly_score_t
    + β_3 sequence_risk_t
    + β_4 data_sensitivity_t
    + β_5 identity_risk_t
    + β_6 tool_chain_risk_t
```

Then:

```text
P_detect(t) = σ(z_t - θ)
```

Where:

```text
σ(x) = 1 / (1 + e^-x)
θ = detection threshold
```

This captures the basic shape:

```text
below threshold → little detection
near threshold → detection probability rises quickly
above threshold → detection saturates
```

So:

> **Parallelism buys exploration and sells stealth.**

The value of parallelism depends on whether increased path discovery outweighs increased detection and containment probability.

---

## 10. The race is symmetric, but the burden is not

Both attackers and defenders can automate.

So the framework should not assume:

```text
offense goes machine-speed
defense stays human-speed
```

The race is symmetric at the automation layer:

```text
offense = adaptive path discovery toward impact
defense = adaptive detection, governance, and containment toward interruption
```

But the burden is asymmetric at the coverage layer.

Attackers need one viable path.

Defenders need adequate coverage across many possible paths.

So the correct statement is:

> **Agentic AI does not structurally guarantee offensive advantage. It increases tempo and adaptiveness for whichever side automates effectively. The asymmetry appears when offense automates adaptive exploration faster than defense can observe, govern, and contain.**

This is a better budget argument than:

```text
AI is new, so give us money.
```

The better argument is:

```text
If offensive exploration becomes machine-speed, defensive detection and containment must also become machine-speed.
```

And:

```text
Detection automation alone is insufficient if containment authority remains human-speed.
```

---

## 11. Total risk requires an interaction term

A useful conceptual split is:

```text
conventional cyber under agentic tempo
AI-native control-surface risk
```

But they are not independent.

So total risk should be written:

```text
R_total =
  R_conventional_tempo
+ R_AI_native
+ R_interaction
```

Where:

```text
R_interaction = cross-amplification between AI-native failures and conventional cyber paths
```

Examples:

```text
prompt injection → unsafe tool use → conventional data access
memory poisoning → bad plan → credentialed SaaS action
RAG poisoning → wrong context → cloud misconfiguration
agent identity gap → unclear delegation → incident response delay
tool authorization failure → conventional lateral movement path
```

So the two-bucket model is analytically useful, but budgeting must not separate the buckets too cleanly.

The operational warning is:

> **AI-native control-surface failures can become delivery mechanisms for conventional cyber impact.**

---

## 12. AI-native risk is a control-surface chain

Define:

```text
U = untrusted or semi-trusted input reaches the agent control surface
C = that input influences context, plan, memory, retrieval, or tool choice
A = tool/delegation policy permits an unsafe action chain
X = material impact occurs
G = governance/detection/containment stops the chain before impact
```

Then:

```text
R_AI_native = E[Impact | 𝔈_AI] × P(𝔈_AI)
```

And:

```text
P(𝔈_AI)
= P(U)
× P(C | U)
× P(A | C, U)
× P(X | A, C, U)
× P(τ_X < τ_G | X, A, C, U)
```

This is a chain-rule decomposition, not an independence claim.

In real systems, these terms are coupled.

A single weak design can collapse several gates at once:

```text
indirect prompt injection
+ weak context isolation
+ broad tool authorization
= U → C → A in one step
```

So the chain should be read as:

> **These are the conceptual gates a safe agentic system should enforce. Weak systems may collapse several gates at once.**

---

## 13. The two-bucket security model

The mature model separates two layers without pretending they are independent.

```text
Total AI-era risk =
  conventional cyber under agentic tempo
+ AI-native control-surface risk
+ interaction risk
```

### Bucket 1: Conventional cyber under agentic tempo

This includes familiar risks:

```text
credential abuse
API abuse
phishing
cloud misconfiguration
exfiltration
lateral movement
vulnerability discovery
endpoint activity
SaaS abuse
```

For this bucket, the existing control families still map:

```text
identity
segmentation
EDR
SIEM / SOAR
DLP
data governance
incident response
least privilege
secure SDLC
rate limiting
```

What changes is cadence, scale, and adaptive throughput.

You now need:

```text
faster detection
faster containment
faster privilege revocation
faster blast-radius reduction
faster triage
faster patching
better automation
```

This is not an entirely new program.

It is the existing program retuned for machine-speed conditions.

### Bucket 2: AI-native control-surface risk

This is where net-new control work is most defensible.

These risks exist because the AI system itself has a control loop:

```text
prompt injection
indirect prompt injection
context poisoning
memory poisoning
tool authorization failure
agent identity gaps
delegated authority failure
RAG poisoning or leakage
system prompt leakage
model/tool supply chain
objective-level policy gaps
control-loop observability gaps
```

This is where you need new controls, new SMEs, and new budget.

Not because HTTP changed.

Because the thing deciding how to use HTTP changed.

---

## 14. Field validation: real AI systems are ecosystems, not chat boxes

This is no longer theoretical.

Real enterprise AI systems are rarely just:

```text
User → Chatbot → Response
```

They are increasingly ecosystems:

```text
front-end applications
RAG systems
multiple models
agents
tool calls
workflow orchestrators
prompt caches
logging and observability systems
document parsers
SaaS APIs
Slack / Teams integrations
command-line or code execution tools
human review workflows
downstream internal applications
```

Assessments of live enterprise AI environments consistently show that the relevant security boundary is not the model alone. The risk emerges from the interaction between untrusted inputs, trusted AI systems, retrieved context, tools, memory, data stores, observability layers, applications, human workflows, and downstream systems.

The model is not the whole system.

The prompt is not the whole system.

The request is not the whole system.

The risk is created by the system path:

```text
input → interpretation → retrieval → planning → tool use → memory → downstream action
```

The security primitive may be familiar.

The system path is not.

---

## 15. AI security is stack security

The right model is not a simple timeline:

```text
Traditional IT → AppSec → Cloud → LLM → Agentic AI
```

That implies replacement.

The better model is a stack:

```text
Agentic AI Security
LLM Application Security
Cloud / SaaS Security
Application & Web Security
Traditional IT Security
```

Each layer still matters.

Agentic AI sits on top because it can orchestrate, chain, and amplify weaknesses in each layer below it.

### Traditional IT Security

Networks, endpoints, identity, perimeter, devices, access, monitoring.

### Application & Web Security

Code flaws, authentication, authorization, injection, business logic abuse.

### Cloud / SaaS Security

APIs, IAM sprawl, misconfiguration, tenant boundaries, managed services, data exposure.

### LLM Application Security

Prompt injection, model misuse, unsafe output, data leakage, context poisoning, RAG leakage.

### Agentic AI Security

Goal-driven autonomy, tool use, memory, cross-system action, delegated authority, adaptive behavior.

The agentic layer is not “next after cloud.”

It is the layer that can coordinate across cloud, SaaS, identity, data, application, and human workflow surfaces.

Agentic risk compounds existing weaknesses.

It does not replace them.

---

## 16. The input plane is now a first-class attack surface

In traditional application security, we care about input.

In AI systems, the input plane expands dramatically.

Input is no longer just:

```text
a form field
an API parameter
a file upload
```

Input can be:

```text
chat messages
uploaded documents
PDFs
scanned files
metadata
RAG corpora
Slack messages
Teams messages
emails
tickets
browser pages
IoCs
URLs
logs
tool outputs
observability traces
memory records
training examples
human review artifacts
```

In live AI systems, security testers increasingly begin by asking:

```text
Where can text, documents, metadata, or external content enter this system?
Where can that content travel?
What can it influence?
Can it reach a model, memory store, RAG corpus, tool call, human reviewer, or downstream application?
```

This matters because, in agentic systems:

> **Any input that can influence planning, memory, tool use, retrieval, downstream rendering, or action is security-relevant.**

The old input validation question was:

```text
Can this input exploit the parser or application?
```

The agentic input question is:

```text
Can this input influence the agent’s objective, plan, memory, tool choice, data access, or downstream action?
```

Input is no longer just data.

Input can become influence.

---

## 17. Prompt injection is control-loop manipulation

Prompt injection is often minimized as “just injection.”

That is only partly right.

Against a simple chatbot, prompt injection may manipulate output.

Against an agentic system, prompt injection can manipulate behavior.

It can affect:

```text
goal interpretation
plan generation
tool selection
memory writes
data retrieval
API calls
external communications
downstream workflows
```

The serious enterprise risk is not merely that a model says the wrong thing.

The serious risk is that malicious or untrusted content can influence what a trusted AI system does.

Prompt injection becomes materially more serious when the model has:

```text
tools
memory
authority
retrieval
business context
downstream effects
```

The issue is not merely:

```text
Can the model be tricked into saying the wrong thing?
```

The issue is:

```text
Can the model be tricked into doing the wrong thing?
```

Prompt injection into an agent is not just text manipulation.

It is control-loop manipulation.

---

## 18. The confused deputy problem is now an enterprise AI problem

The most dangerous enterprise scenario is not necessarily an external AI attacking from outside.

The more subtle scenario is:

> An adversary, malicious document, compromised user, poisoned memory, or indirect prompt injection steers an internal enterprise agent into misusing its legitimate authority.

This is the agentic confused deputy problem.

The call is coming from inside the house.

The agent may use:

```text
approved APIs
valid OAuth tokens
normal SaaS integrations
internal search
employee permissions
browser automation
ticketing workflows
document summarization
expected collaboration tools
```

Traditional defenses may see:

```text
valid user
valid agent
valid token
valid tool
valid API
valid workflow
valid internal system
```

But the objective may be unauthorized.

So agentic AI security must ask not only:

```text
Was this action allowed?
```

but also:

```text
Was this objective authorized?
Was this delegation valid?
Was this tool chain appropriate?
Was this data access consistent with user intent?
Was this retry behavior acceptable?
Was this internal access hijacked?
```

Agentic AI turns confused deputy risk into a first-class enterprise security concern because agents can use trusted internal authority while being influenced by untrusted or semi-trusted content.

---

## 19. A system prompt is not an access-control boundary

Prompt engineering can express policy.

It cannot be the policy enforcement layer.

A system prompt can say:

```text
Only show fields A through F.
Never reveal the API key.
Do not access confidential data.
Do not call external tools.
```

But that is not the same as enforcing policy at the database, retrieval, authorization, tool, memory, or output boundary.

Live AI assessments repeatedly show the danger of relying on prompt instructions to enforce security policy. When sensitive data is retrievable by the system, when tools have broad authority, or when internal business logic is encoded directly into prompts, attackers may be able to manipulate the model into exposing information or taking actions that the application designers did not intend.

The principle is simple:

> **A system prompt is not an access-control boundary.**

And:

> **A guardrail can refuse a sentence. Governance must constrain an action chain.**

Agentic governance must happen at multiple layers:

```text
identity
authorization
retrieval
tool policy
data classification
memory
output
approval
logging
runtime monitoring
```

The prompt can describe the rule.

The system must enforce the rule.

---

## 20. Guardrails are not governance

Guardrails matter.

Classifiers matter.

Model refusals matter.

Input and output filters matter.

But they are not enough.

Guardrails tend to operate around text classification, refusal, or content filtering.

Agentic risk often lives in the chain:

```text
goal → context → plan → tool → observation → memory → retry → action
```

A guardrail might block one response.

Governance must answer a broader set of questions:

```text
Should this agent pursue this objective?
Should it use this tool?
Should it combine these data sources?
Should it retry after denial?
Should it store this memory?
Should it call an external system?
Should it act under this user’s authority?
Should it continue after repeated failures?
```

Security experience with AI systems increasingly shows that content filters, refusals, and prompt-level protections are useful but incomplete. They can reduce risk at the text layer, but they do not, by themselves, govern the agentic loop.

So the answer is not:

```text
Buy a guardrail and you are done.
```

The answer is:

```text
Use guardrails, but govern the loop.
```

---

## 21. Non-determinism changes testing and detection

LLM and agentic systems are probabilistic.

That matters.

A traditional exploit often behaves like:

```text
payload works → payload works again
payload fails → payload fails again
```

AI systems often behave more like:

```text
payload may work on attempt 3
payload may fail on attempt 1
same prompt may produce different behavior
slight variants may change outcome
context may shift the result
```

This creates a new testing implication:

> **Exploitability may be probabilistic over repeated attempts.**

It also creates a new detection implication:

> **A single failed attempt may not mean the system is safe.**

Agentic risk must be modeled across:

```text
retries
variants
prompt mutations
context changes
sampling effects
capability changes
tool availability
memory state
```

This is why the companion demo uses a Monte Carlo curve.

The point is not that the agent is simply faster.

The point is that the agentic curve bends because capability improves path quality, alternate-route discovery, and adaptation after failure.

The comparative curve should show a near-flat static curve and a rising agent curve. The caption should make the interpretation explicit:

> **This is path-quality, not speed.**

---

## 22. Business context matters

Many real AI security failures are not generic.

They are business-context-sensitive.

A naïve prompt may fail.  
A plausible business request may succeed.  
A generic test case may be blocked.  
A context-aware instruction embedded in a normal workflow may reach the agent, the retrieval layer, the tool chain, or the human reviewer.

That matters because enterprise agents do not operate in empty space.

They operate in business context:

```text
customer records
support tickets
finance reports
engineering notes
security alerts
Slack threads
CRM records
DevOps workflows
internal documents
project names
employee identities
approval processes
```

An agent is dangerous not because it randomly tries tools.

It is dangerous because it can use context.

For example:

```text
The direct finance API failed.
The agent learns the report name.
The agent identifies the owning team.
The agent finds a related ticket.
The agent searches a document index.
The agent finds an alternate workflow.
The agent retries through a legitimate internal path.
```

That is not merely speed.

That is context-aware path discovery.

The security question becomes:

```text
Can the system distinguish authorized business reasoning
from hijacked or adversarial objective pursuit?
```

---

## 23. Agentic security must cover the data lifecycle

The risk is not only runtime.

Content that enters an AI system can become:

```text
retrieved context
memory
training data
fine-tuning data
RAG corpus content
audit data
observability logs
human review artifacts
evaluation data
downstream application content
```

This creates a lifecycle problem.

A malicious instruction, sensitive document, poisoned example, or unsafe artifact may not only affect the current session. It may persist, reappear, be summarized, be embedded, be indexed, be reviewed by humans, be written to logs, or be incorporated into future system behavior.

Agentic security must therefore cover the data lifecycle, not only the live session.

Every transition is a security boundary:

```text
input → retrieval
input → memory
input → training
input → logs
input → human review
input → downstream app
input → external tool
```

The agentic question is:

```text
Where can this content travel?
What can it influence?
How long can it persist?
Can it affect future decisions?
Can it cross from untrusted input into trusted context?
```

A system is not safe merely because the live response looked harmless.

The content may still become future influence.

---

## 24. Data classification becomes runtime policy

AI makes data classification newly urgent because data is increasingly mixed, transformed, summarized, retrieved, and moved across systems.

Agentic AI sharpens the problem.

A traditional system might access one dataset.

An agent can:

```text
read an internal document
summarize it
combine it with Slack context
query a ticket
cross-reference a CRM record
retrieve source code
store a memory
generate an external email
invoke another tool
```

The data may change form at every step.

So classification cannot be only a label on a database.

It must become runtime policy.

Agentic systems need to know:

```text
What data class is this?
Where did it come from?
What has it been combined with?
Can it be summarized?
Can it be stored?
Can it be sent externally?
Can it be used in a tool call?
Can it influence memory?
Can it influence future actions?
```

Data governance becomes part of the control loop.

The question is no longer only:

```text
Who can access this data?
```

It is also:

```text
What can an agent do with this data once accessed?
Where can it move?
What can it be combined with?
Can it become memory?
Can it become output?
Can it become future context?
```

---

## 25. The AI worker needs identity

AI workers are beginning to operate beside human workers.

They appear in collaboration tools, security tools, development tools, support workflows, productivity suites, data platforms, and internal applications.

That means agents need to be treated as accountable actors.

Every production agent should have an identity card:

```text
Agent name:
Owner:
Business purpose:
Allowed goals:
Forbidden goals:
Tools:
Data classes:
Delegated authority:
Memory scope:
Approval thresholds:
Logging requirements:
Kill switch:
Review cadence:
```

The enterprise cannot treat agents as invisible UI features.

An agent is not merely a chat interface.

An agent is an actor.

Actors need:

```text
identity
scope
delegation
boundaries
accountability
auditability
revocation
```

The old question was:

```text
Which user did this?
```

The new question is:

```text
Which agent did this, acting for which user, under which delegated authority, pursuing which goal?
```

---

## 26. Visibility must include the loop, not just the event

Traditional logs might show:

```text
user_id
timestamp
API endpoint
status code
resource
IP address
device
```

That is useful.

But for agentic systems, it is not enough.

Agentic traces must also capture:

```text
agent identity
human principal
delegated authority
user-stated goal
system goal constraints
retrieved context
tool choice
tool chain
failed attempts
retry behavior
memory reads
memory writes
data sensitivity crossings
approval decisions
final action
```

The security question shifts from:

```text
Did an event happen?
```

to:

```text
What objective was being pursued, and how did the system adapt toward it?
```

This is the explainability requirement for agentic security.

If the agent cannot show its work, the organization cannot govern its work.

If the organization cannot reconstruct the loop, it cannot distinguish:

```text
valid action from valid objective
authorized access from authorized purpose
normal tool use from hijacked delegation
ordinary failure from adaptive bypass
```

Visibility has to move from event logging to control-loop observability.

---

## 27. The proof method

This manifesto should not rely only on rhetoric.

It should be demonstrable.

The companion demo exists to prove a narrow point:

> Given the same goal, same first tool, same initial denial, and same primitive actions, a static automation stops while an agentic loop adapts.

The demo should not claim:

```text
This toy agent is a frontier AI model.
```

It should claim:

```text
This toy agent makes the control loop visible.
```

That is enough.

Because the point is not to prove that the toy agent is intelligent.

The point is to show that adding observation, state, retry, and alternate-path selection changes the security behavior.

---

## 28. The demo’s central scene

The demo should make this moment unavoidable:

```text
Both actors receive: 403 Forbidden
```

Then:

```text
Static automation: stops
Agentic executor: interprets denial as feedback and continues
```

This is the moment where the old model breaks.

The page should say:

> **The difference is not speed. The difference is what happens after failure.**

The Monte Carlo curve should reinforce the same idea.

It should not show that the agent wins because it is faster.

It should show that, across capability levels, the static success rate stays relatively flat while the agentic success rate rises because better capability improves path selection, retry quality, business-context use, and alternate-route discovery.

That is the evidence layer of the manifesto.

---

## 29. Demo updates implied by the hardened model

The demo should evolve with the math.

### 1. Equal action budget mode

Both actors receive the same step budget.

This proves:

```text
The agent does not win because it acts faster.
The agent wins, when it wins, because it uses feedback differently.
```

### 2. Probabilistic edges

Instead of only hard-coded allowed or blocked paths, each path should show:

```text
residual reachability
control strength
telemetry cost
approval requirement
data sensitivity
```

This makes `G_C` realistic.

### 3. Explicit goal

The trace should show the goal clearly.

Example:

```text
goal = retrieve approved report
```

or:

```text
goal = locate sensitive document
```

The agent policy should be visibly goal-conditioned.

### 4. Telemetry and detection meter

Show:

```text
event count
denials
tool calls
sequence risk
anomaly score
detection probability
```

Parallel attempts should increase both exploration and detection evidence.

### 5. Separate containment slider

Separate:

```text
visibility / detection
containment authority
```

The demo should show that great detection with slow containment can still lose.

### 6. Interaction term example

Show an AI-native failure becoming a conventional cyber path:

```text
indirect prompt injection → unsafe tool call → credentialed internal data access
```

This prevents finance or leadership from treating the two risk buckets as cleanly separable.

---

## 30. Current automation is not perfect — and that does not weaken the argument

We should not overclaim.

Current automated AI security testing is not a full replacement for expert human testing.

Many high-quality AI attacks still require business context, creativity, manual iteration, and deep understanding of the target system. Automated scanners and evaluation frameworks can be useful, but they often struggle with context-specific attacks, multi-step workflows, and nuanced enterprise abuse cases.

That does not weaken the framework.

It strengthens the capability-curve argument.

The manifesto should not say:

```text
Agents already replace expert red teamers.
```

It should say:

```text
Agentic capability is a moving frontier.
```

The current gap between expert human testing and automated agentic testing is not a reason to dismiss the risk.

It is a measure of where the capability curve is headed.

The risk is not that today’s agent is perfect.

The risk is that adaptive task-completion capability is becoming:

```text
cheaper
faster
more available
more integrated
more persistent
more tool-connected
more business-context-aware
```

Security models should be built for the direction of travel, not just the current baseline.

---

## 31. The controls this implies

If the risk is the loop, then controls must govern the loop.

Agentic AI security needs controls across at least twelve domains.

### 1. Agent identity

Every agent must have a distinct identity.

Not just:

```text
user = jane@company.com
```

But:

```text
agent = finance-research-agent
acting_for = jane@company.com
authority = delegated
scope = finance docs, Slack search, ticket lookup
```

### 2. Delegated authority

The agent should not inherit all user permissions by default.

It should receive constrained, purpose-bound, time-bound authority.

### 3. Tool-use policy

Tools should be available based on goal, context, data sensitivity, risk, and approval level.

Not all tools should be callable just because the user has access.

### 4. Objective-level policy

The system must evaluate whether the goal itself is allowed.

A permitted API call may still serve a prohibited objective.

### 5. Memory integrity

Memory must be treated as a security boundary.

It can be poisoned, over-retained, cross-contaminated, or misused.

### 6. Context isolation

Instructions, retrieved content, tool output, user input, and system policy must be separated.

External content should not be allowed to silently rewrite the agent’s operating instructions.

### 7. Retry and adaptation limits

Repeated denials should not automatically trigger unbounded exploration.

Some failures should stop the loop.

### 8. Data boundary enforcement

The agent must understand data classification across the chain, not just at the source.

It must not be able to launder confidential data through summarization, transformation, memory, or tool chaining.

### 9. Sequence detection

Detection must look for suspicious chains, not just suspicious events.

One request may be normal.

The sequence may not be.

### 10. Containment authority

Detection is not containment.

Sensitive agentic workflows need explicit authority paths for:

```text
session revocation
agent shutdown
tool disablement
connector revocation
memory quarantine
approval hold
blast-radius reduction
```

Machine-speed detection without machine-speed containment can still lose the race.

### 11. Human approval

Sensitive actions should require human approval before execution, especially when the agent is crossing data boundaries, invoking external tools, changing permissions, sending communications, modifying code, or taking irreversible action.

### 12. Input-plane governance

Every source of text, document, metadata, retrieved content, tool output, and memory must be treated as potential influence on the agent.

Input security is no longer only about application parsing.

It is about influence over the control loop.

### 13. Lifecycle governance

Content must be tracked across runtime, memory, logs, retrieval, evaluation, fine-tuning, human review, and downstream systems.

Data that enters the AI system should not silently become permanent influence.

---

## 32. Governance must move from actions to objectives

Traditional governance asks:

```text
Can this user access this system?
Can this API call happen?
Can this data be downloaded?
Can this command run?
```

Agentic governance must also ask:

```text
Should this agent pursue this goal?
Should this agent use this tool for this purpose?
Should this data be combined with that data?
Should this denial trigger a retry or a stop?
Should this content enter memory?
Should this action require approval?
Should this chain be allowed even if each individual step is allowed?
```

Governance cannot stop at individual actions.

It must govern the autonomous loop.

Agentic governance needs to cover:

```text
goal governance
tool governance
data governance
memory governance
delegation governance
chain governance
retry governance
approval governance
explainability governance
lifecycle governance
containment governance
```

This is the difference between securing an API call and securing an autonomous actor.

---

## 33. The defensive use case

This manifesto is not anti-agent.

The same properties that create risk also create enormous defensive value.

A governed defensive agent can:

```text
find vulnerabilities
triage alerts
summarize incidents
propose patches
verify fixes
map attack surfaces
check secure patterns
update inventories
generate risk explanations
```

If attackers can use AI to increase speed, scale, and adaptability, defenders can use AI as well.

The right conclusion is not:

```text
Do not use agents.
```

The right conclusion is:

```text
Do not deploy autonomous loops without governing the loop.
```

A safe defensive loop might look like:

```text
Find issue → Propose fix → Verify → Explain → Request approval → Apply → Log
```

An unsafe loop looks like:

```text
Goal → Search everything → Chain tools → Retry around denials → Act externally → Log only the final request
```

The difference is governance.

The goal is not to stop agentic systems.

The goal is to make them accountable, constrained, observable, and aligned with authorized objectives.

---

## 34. The maturity model

### Level 0: No agent awareness

Agents are treated as ordinary applications or chatbots.

```text
No agent identity
No tool-chain logs
No goal governance
No memory controls
No approval boundaries
No containment authority
```

### Level 1: Basic containment

Agents have limited tools, narrow access, and basic logging.

Sensitive actions are manually reviewed.

### Level 2: Agent identity and delegation

Agents have distinct identities, owners, scopes, and delegated authority.

Logs distinguish:

```text
human
agent
tool
resource
objective
```

### Level 3: Tool, input, and data governance

Tool use is policy-gated by purpose, context, and data sensitivity.

Input sources are classified by influence risk.

Data boundaries are enforced across multi-step chains.

### Level 4: Control-loop observability

The organization can reconstruct:

```text
goal
plan
context
tool chain
observations
memory reads/writes
retries
approval points
final action
```

### Level 5: Adaptive governance

Policies dynamically constrain agents based on:

```text
behavior
risk
sensitivity
repeated denials
anomalous tool chaining
objective drift
data-boundary crossings
memory contamination
external content influence
containment readiness
```

The organization governs not just actions, but autonomous pursuit.

---

## 35. The language we should use

Use this:

```text
Same primitives. New controller. Revised risk model.
```

Use this:

```text
Existing controls govern the probabilistic action graph. Agentic security governs the goal-directed controller searching it.
```

Use this:

```text
The primitive did not change. The controller did.
```

Use this:

```text
The difference is not speed. The difference is what happens after failure.
```

Use this:

```text
Failure becomes feedback.
```

Use this:

```text
A script executes steps. An agent pursues objectives.
```

Use this:

```text
The request may be familiar. The autonomous sequence is not.
```

Use this:

```text
Conventional cyber becomes a machine-speed cadence problem. AI-native agent surfaces create new control requirements.
```

Use this:

```text
Parallelism buys exploration and sells stealth.
```

Use this:

```text
Detection automation alone is insufficient if containment authority remains human-speed.
```

Use this:

```text
We are not replacing fundamentals. We are extending them to govern the loop.
```

Use this:

```text
A system prompt is not an access-control boundary.
```

Use this:

```text
A guardrail can refuse a sentence. Governance must constrain an action chain.
```

Use this:

```text
The model is not the boundary. The AI ecosystem is the boundary.
```

Use this:

```text
Input is no longer just data. Input can become influence.
```

---

## 36. The language we should avoid

Avoid:

```text
Everything is new.
```

That is false and easy to attack.

Avoid:

```text
Existing controls do not matter.
```

They matter.

Avoid:

```text
Agentic AI structurally guarantees offensive advantage.
```

It does not. Defenders can automate too.

Avoid:

```text
Parallelism is a free multiplier.
```

It is not. It generates telemetry.

Avoid:

```text
AI has IQ like a human.
```

Use:

```text
autonomous task-completion capability
effective adversarial throughput
capability density per dollar/hour
```

Avoid:

```text
Agents are always malicious.
```

They are not.

Avoid:

```text
This is magic.
```

It is not magic. It is a control loop.

Avoid:

```text
Prompt injection is just injection.
```

Say:

```text
Prompt injection into an agent can manipulate planning, memory, tool use, and delegated action.
```

Avoid:

```text
Cloud was totally new, therefore agents are totally new.
```

Say:

```text
Cloud had old primitives but a new operating model. Agentic AI is the same kind of shift.
```

Avoid:

```text
Guardrails solve it.
```

Say:

```text
Guardrails are useful controls, but agentic security requires loop governance.
```

Avoid:

```text
These equations produce the risk number.
```

Say:

```text
These equations are a reasoning scaffold. Quantification requires calibration.
```

---

## 37. The answer to “curl is still curl”

Yes.

`curl` is still `curl`.

But that is not the security question.

The security question is:

```text
Who or what decides the next curl?
What goal is it pursuing?
Why was it called?
What context influenced the decision?
What failed before this?
What will the agent try next?
What authority is it using?
What data boundary is it crossing?
How much telemetry did it generate?
Can defenders contain the chain quickly enough?
Can the sequence be reconstructed?
Can the loop be stopped?
```

A single request can look normal.

The sequence can be malicious.

A single tool call can be authorized.

The objective can be unauthorized.

A single credential can be valid.

The delegation can be hijacked.

A single API event can be old.

The autonomous control loop is new.

---

## 38. The answer to “this is not a new problem”

At the highest level of abstraction, almost nothing in security is new.

Cloud was “just servers, APIs, and identity.”

Mobile was “just endpoint security.”

SaaS was “just web apps.”

Kubernetes was “just Linux, containers, and networking.”

Supply chain was “just third-party trust.”

Ransomware was “just malware plus encryption plus extortion.”

Prompt injection is “just injection.”

Agentic AI is “just automation.”

All of those statements contain some truth.

All of them miss the operating-model change.

Agentic AI is not new because every ingredient is new.

Agentic AI is new because the composition changes system behavior.

A precursor is not equivalence.

An old primitive in a new control loop can create a new security domain.

But we should be precise:

```text
Conventional cyber under agentic tempo is a retuning of existing control families.
AI-native control-surface risk is where net-new controls appear.
The interaction term is where the two amplify each other.
```

That is the defensible version.

---

## 39. The final manifesto

We believe agentic AI security must be understood at the controller layer.

The industry will be tempted to minimize the shift by pointing to familiar primitives:

```text
HTTP requests
credentials
APIs
automation
injection
authorization
logging
data access
file upload
workflow abuse
```

That instinct is understandable.

It is also incomplete.

Security is not only about primitives.

Security is about the system that chooses, sequences, adapts, authorizes, and explains the use of those primitives.

Agentic AI changes that system.

It moves us from static execution to adaptive objective pursuit.

It moves us from single actions to tool chains.

It moves us from request authorization to delegated intent.

It moves us from prompt safety to ecosystem security.

It moves us from output inspection to loop governance.

It moves us from input validation to input-plane governance.

It moves us from data labels to runtime data-boundary enforcement.

It moves us from event logging to control-loop observability.

It moves us from detection-only thinking to detection-plus-containment thinking.

It moves us from “did this API call succeed?” to “should this agent have pursued this objective in this way?”

The old fundamentals still matter.

But they must be extended.

We still need identity.  
Now we also need agent identity.

We still need authorization.  
Now we also need delegated authority and objective-level policy.

We still need logging.  
Now we also need goal, plan, context, memory, tool-chain, and retry traces.

We still need data classification.  
Now we also need runtime enforcement across transformations, memory, and multi-tool chains.

We still need AppSec.  
Now we also need prompt, context, memory, retrieval, and tool-use security.

We still need cloud security.  
Now we also need to understand how agents compose cloud and SaaS permissions into workflows.

We still need detection.  
Now we also need governance of autonomous search.

We still need containment.  
Now we need containment authority that can keep pace with machine-speed action chains.

We still need guardrails.  
Now we also need policy enforcement around actions and chains.

We still need humans.  
Now humans must supervise systems that can act.

The mature position is not:

```text
Everything is new.
```

The mature position is:

```text
The primitives are familiar, but the controller and operating model have changed.
```

And when the controller and operating model change, the risk model changes.

That is why agentic AI security is not merely:

```text
the same attacks, faster
```

It is:

```text
same primitives
+ goal-directed controller
+ tool access
+ memory
+ feedback
+ business context
+ delegated authority
+ adaptive retries
+ ecosystem integration
+ imperfect controls
+ defender containment constraints
= revised operational risk model
```

Or, in the shortest possible form:

> **Existing controls govern the probabilistic action graph. Agentic security governs the goal-directed controller searching it.**

---

## Sources and grounding

This manifesto synthesizes three streams of evidence and design work:

1. **Practical enterprise AI security assessment patterns.** Live AI systems increasingly span multiple models, agents, RAG, prompt caches, logging and observability layers, workflow orchestration, tool calls, SaaS APIs, document processing, collaboration integrations, and downstream business applications. These systems are assessed as ecosystems, not isolated chat boxes.

2. **Security leadership observations about AI-driven change.** AI is increasing the speed, volume, and complexity of software and security work. It is making data classification, explainability, governance, human critical thinking, AI workers, and AI-augmented security teams newly urgent.

3. **The companion agentic security simulation.** The demo is designed to make the control-loop distinction observable: two actors begin with the same goal, same first primitive, and same initial denial; the static automation stops, while the agentic executor treats failure as feedback and continues. The comparative curve is designed to show path-quality, not speed.

For public publication, cite original public talks, papers, demos, or assessment writeups where available. For internal use, preserve the assessment notes, talk transcripts, and demo requirements that grounded this draft.
