---
name: legal-comms-check
description: Check and revise communications to, with, or cc'ing Legal (in-house attorneys, outside counsel) for U.S. attorney-client privilege best practices before they are sent. Use whenever the user is drafting, writing, reviewing, revising, or scheduling an email, Slack/Teams/chat message, meeting invite or agenda, document, or note that involves a lawyer or a legal topic — e.g. "help me email Legal about the vendor dispute", "draft a Slack to our attorney", "set up a meeting with counsel on the new launch", "review this before I send it to legal", "should I mark this privileged?". Apply this skill even when the user does not mention "privilege" at all — any communication directed at, copying, or requesting input from an attorney, or about legal risk, should be run through it. NOT a substitute for actual legal advice or an attorney's final privilege determination; NOT for communications with no legal/attorney involvement.
when_to_use: The user is preparing, revising, or scheduling any communication (email, chat message, meeting invite/agenda, document, or notes) that goes to / is copied to / requests input from an attorney, or that concerns legal risk or privilege. Triggers on "email/slack/message/meeting with legal/counsel/attorney", "review this for legal", "should this be privileged/marked P&C". NOT for non-legal communications, and NOT a replacement for a lawyer's advice or privilege call.
---

# Legal Communications Privilege Check

Help the user communicate with Legal in a way that protects genuinely
privileged content and avoids over-marking — because (1) recent court rulings
have narrowed privilege, and (2) over-marking ordinary business material as
"privileged" creates legal and reputational risk and weakens the protection of
material that truly deserves it.

**The golden rule:** the attorney-client privilege protects a communication only
when its **primary purpose is to request or provide legal advice**. Involving a
lawyer, or stamping "Privileged," does not by itself create privilege.

## When this triggers

Any time the user is drafting, revising, or scheduling a communication that an
attorney will send, receive, be copied on, or be asked to weigh in on — email,
Slack/Teams/chat, meeting invite or agenda, internal doc, or meeting notes —
**or** asks whether something should be marked privileged. Apply it proactively
even if the user never says the word "privilege."

## Procedure

1. **Identify the communication type and intent.** Is the user actually seeking
   *legal advice* (legal implications, legal risk, compliance-with-law
   questions), or *business* input (cost, strategy, operations, PR, editing)?
   This determines everything.
2. **Read `references/privilege-playbook.md`** and assess the draft against the
   checklist there. That file holds the full ruleset, marking conventions,
   decision guide, and revision patterns — consult it every time; do not rely on
   memory.
3. **Report findings** plainly, grouped by severity:
   - 🔴 **Fix before sending** — e.g. over-marking, mixing legal+business with no
     signposting, vague "please advise," wide distribution of legal advice,
     sharing privileged content with third parties.
   - 🟡 **Consider** — e.g. could be clearer/more specific, marking could be more
     precise, legal vs business could be separated.
   - 🟢 **Good** — what the draft already does right.
4. **Produce a revised draft** that follows best practice (correct marking,
   specific legal-advice request, legal content separated/signposted,
   appropriately narrow distribution). Show it clearly so the user can use it
   directly. If scheduling a meeting, fix the title/agenda and the privilege
   posture of any notes.
5. **Always append the standard caveat** (see below).

## Quick checklist (full detail in the playbook)

- **Primary purpose:** Is this primarily seeking/giving *legal advice*? If not,
  it is generally **not** privileged — don't mark it privileged.
- **Specific ask:** Does it make a clear, specific request for legal advice
  (e.g. *"Attorney X, do you see any legal risks to this approach?"*) rather than
  vague "please advise," "seeking legal advice," or "maintaining privilege"?
- **Legal vs business:** If it mixes both, is the legal advice signposted
  ("Legal advises…") or in a separate labeled section ("Legal Considerations")
  so it can be identified and protected?
- **Marking:** Primarily legal → "Privileged & Confidential." Mixed →
  "Confidential – Contains Legal Advice" (+ signposting). Sensitive business /
  deal docs → "Company Confidential," **not** "Privileged."
- **Visibility ≠ privilege:** Just giving Legal an FYI? Don't mark it P&C and
  don't add a lawyer with a shorthand privilege tag.
- **Distribution:** Legal advice goes only to people who need it for their job —
  not big DLs, listservs, or broad Slack/Teams channels; not into AI tools
  unless Legal approved.
- **Third parties:** Never share legal advice/work product outside the company
  (ex-employees, suppliers, contractors, sellers) without Legal's approval.
- **Facts aren't protected:** Sensitive facts don't become privileged by being
  told to a lawyer or by stamping "Privileged" on the thread.
- **Meeting notes:** Not privileged just because a lawyer attended; mark and
  signpost legal-advice portions, avoid verbatim quotes, name the advising
  attorney.

## How to revise (patterns)

- Replace vague asks with a pointed legal question naming the attorney and the
  specific risk/law/decision.
- Split a mixed message: business ask in the body; legal questions in a clearly
  labeled "Legal Considerations" block or a separate message to counsel.
- Downgrade an over-broad "Privileged & Confidential" to "Company Confidential"
  (or no marking) when the purpose is business.
- Trim recipients to need-to-know; move broad audiences off the legal-advice
  thread.
- For a meeting: make the invite title/agenda state whether the primary purpose
  is legal advice, and set the notes posture accordingly.

## Standard caveat (always include in output)

> This is general privilege-hygiene guidance based on internal training, **not
> legal advice and not a privilege determination**. Attorneys take the lead on
> privilege calls — if anything here is sensitive or unclear, confirm with your
> legal partner.

## Constraints

- Don't tell the user a communication "is privileged" as a guarantee — frame it
  as whether it *follows best practice* and is *more likely* to be protected.
- Never recommend over-marking to be "safe"; over-marking is itself the risk.
- Privilege is weaker or absent outside the U.S.; flag international sharing and
  point to a country-specific legal POC.
- This skill checks privilege hygiene; it does not answer the underlying legal
  question — that is for an attorney.
