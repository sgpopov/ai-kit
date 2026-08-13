# ADR Basics 3: Creating a Service-level ADRs

Service-level ADRs are created and stored by the teams which own the service. It is suggested that you store the ADRs as part of your codebase, or in a wiki associated with your service.

# Storing in code repository

To add ADRs to your repo:

1. Create a folder in the root of your project or within a \`/docs\` called “ADRs”  
2. Use the template below to create your ADRs. It could be helpful to create a file called “template.md” in your ADR folder for reusability  
3. A best practice is to commit the ADR to your repo along with the code that relates to it. This ensures that the ADR gets reviewed during the Merge Request process  
4. Instead of using a numbering system as we do with System-Level ADRs, a best practice would be to use a date and title as the file name. For example, **2020-06-08-Queue-System.md**.

## Template

```
# Queue System

#### In the context

some medium

#### Facing the need

requirement faced

#### We decided

decision made

#### And against

alternatives discussed

#### To achieve

what you have enabled

#### Accepting that

concessions and assumptions made

#### Supporting links

list of files or links relative to the decision
```

