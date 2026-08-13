# ADR-1: HTTP Request Format for Querying Resources with PHI

| Record | ADR-2 |
| :---- | :---- |
| **Status** | APPROVED |
| **Topic** | HTTP Request Format for Querying Resources with PHI |
| **Owner** | Svilen Popov |
| **Requestor** | Svilen Popov |
| **Requested Date** | Jan 1, 2023 |
| **Decision** | Use POST body for criteria |
| **Decision Date** | Jan 2, 2023 |
| **Sign-off By** | *\<name\> \<name\>* |

# Architecture Decision Record

## In the context

Of enabling an API request to query for resources where the query string could contain PHI

## Facing the need

to avoid leaking PHI or PP data into browser history, server logs, and any other places that could cache URLs

## We decided

to require requests which need to query data utilize **POST** requests where any criteria could contain PHI would reside in the body of the request

## And against

a **GET** request with PGI data on the query string

## To achieve the ability

- to minizming the risk associated with transferring data in a plain-text URL  
- to eliminate the risk that server logging tools will also go sensitive information (PHI)  
- to prevent PHI data storing in the browser history

## Accepting that

The implementation and documentation thereof is up to the service that is responsible for the data

## Example

**✖ Incorrect usage**

```
GET /users?firstName=George
```

**✔ Correct usage**

```
POST /users

{
  "firstName": "George"
}
```

