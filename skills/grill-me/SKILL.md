---
name: grill-me
description: Interviews the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
disable-model-invocation: true
---

# Grill Me

## Overview

A prompt skill that interrogates a plan or design one question at a time, walking every branch of the decision tree until you and the user reach genuine shared understanding.

## When to Use

- The user wants to stress-test a plan or design, or says "grill me"
- A decision has open branches or unstated assumptions worth surfacing before building

Do **not** use it for a quick factual answer, or once the design is already settled — use [[grill-with-docs]] instead when the project keeps a `CONTEXT.md`/ADRs you should challenge against.

## The Prompt

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.

## Verification

The session is complete when every branch of the decision tree is resolved, no open assumptions remain, and the user confirms the shared understanding matches their intent.
