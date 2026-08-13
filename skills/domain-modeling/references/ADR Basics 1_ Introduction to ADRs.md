# ADR Basics 1: Introduction to ADRs

# What is an Architectural Decision Record (ADR)?

An Architectural Decision Record is a lightly structured, plain-spoken record of a software design choice that is architecturally significant. ADRs can be used to encompass choices that are both functional and non-functional in nature. 

An ADR contains several parts:

* The decision that is made  
* Why that decision was made  
* What other options were considered and why they were not chosen  
* Any assumptions that were made which affected the decision  
* Any concessions made as a consequence of the decision

# Why do we create ADRs?

### **To record what, why and when**

We create ADRs to track what decisions were made at a point in time, but more importantly, ADRs help us record **why** a decision was made as well. While the motive of a decision may seem obvious at the time, ADRs live with the system and service for its lifetime. Years later, anyone can reference ADRs to understand the reasons a decision was made, which gives engineers perspective on the systems they are working with.

### **To help onboard engineers to projects**

When an engineer is new to a project (or an organization), they often ask why something works the way it does. ADRs give an accurate accounting of the decisions made and why they were made, which gives new engineers an obvious place to start when they are exploring a new project.

### **To allow for technical debt**

We often make decisions knowing that it is not the best long term decision, but factors such as deadlines, requirements, and varying timelines force those decisions. ADRs allow us to acknowledge those concessions when the decision is made so that they can be referenced and resolved later.

# When is it appropriate to record an ADR?

ADRs should be recorded whenever any architecturally relevant decision is made.

You should record an ADR when

* A new integration pattern is used  
* A new external software package is selected  
* A new configuration pattern is used in a declarative system  
* A new technology is selected to replace an existing one  
* A financial impact will be felt because of the decision (positive or negative)

ADRs **do not** need to be recorded for

* Internal-only software patterns  
* Product requirements, such as the use of new attributes or relationships internal to the project

**An ADR is the result of an architectural decision being made.** Not all architectural decisions require the same level of interrogation.

# Where should I record an ADR?

In this project, we strive to complete ADRs at a system level and a service level. Determining the scope of your decision helps map where to record your ADR.

### **System-level ADRs**

System-level ADRs encompass changes that affect multiple systems or service offerings. For example:

* A new security pattern is identified to communicate service-to-service  
* A configuration change is made to PubSub (a common service)  
* PostgreSQL is added as a supported database technology

Follow ADR Basics 3: Creating a Service-level ADRs to learn how to create a Service-level ADR for your particular service. 

# What does an ADR look like?

We use [Y-Statements](https://medium.com/olzzio/y-statements-10eb07b5a177) to record our choices, which gives a simple, story-like record of our decision.

Similar to the common user story format you are familiar with: 

*As a **\< type of user \>**,*  
*I want **\< some goal \>***  
*so that **\< some reason \>**.*

Y-Statements tell a story of the decision

*In the context of **\< some medium \>**,*  
*Facing the need **\< requirement faced \>**,*  
*We decided **\< decision made \>**,*  
*And against **\< alternatives discussed \>**,*  
*To achieve the ability **\< what you have enabled \>**,*  
*Accepting that **\< concessions and assumptions made \>**.*

# How much detail should an ADR have?

### **Do's**

* Make your ADR succinct and to the point  
* Use plain, simple language  
* Include enough detail where a non-informed engineer can understand the decision

### **Don'ts**

* Overload an ADR to include more than one decision  
* Include implementation details unless they specifically affect the decision made

