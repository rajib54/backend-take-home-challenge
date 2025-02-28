# Take-Home Challenge: URL Stats Aggregation & Reporting API

## Overview

You must build a **FastAPI**-based microservice that handles two primary functions:

1. **Shorten URLs** – The service stores long URLs, returns a short slug, and tracks usage statistics (visits).  
2. **Aggregate/Report** – The service provides an endpoint to query aggregated stats (e.g., total visits per link, top N visited links, etc.).  

Your goal is to design, implement, and deploy this service so we can test it live and evaluate its code and performance characteristics.

**Important**: This brief describes a lot of functionality. If you don't have the time to fully design and implement the features described in this brief that is fine!
Try to immplement a solution:
1. written using fastapi
2. has a database layer
3. can easily be run locally for testing

## Requirements

### 1. Short Link Creation

- **Endpoint**: `POST /shorten`
- **Request Body** (example):
  ```json
  {
    "long_url": "https://www.example.com/very/long/url"
  }
  ```
- **Response** (example):
  ```json
  {
    "slug": "abcd123",
    "short_url": "http://your-service.com/abcd123"
  }
  ```
- Behavior:
  - Store the mapping of slug → original URL in your database.
  - Return a generated slug and the corresponding short URL.
  - Decide whether to reuse an existing slug if the same long_url is posted again or always generate a new slug. Document your choice.
 
### 2. Redirection

- **Endpoint**: GET /{slug}
- **Behavior**:
  - Look up slug in the database.
  - If found, redirect (HTTP 307) to the original long_url.
  - If not found, return 404.
  - Track usage: each time the short URL is accessed, increment a visit counter or store a timestamp record (so we can produce stats).

### 3. Reporting / Analytics
- Provide one or more endpoints to retrieve usage stats:
  - GET /stats – Return the top N links by total visits, or another useful summary.
  - GET /stats/{slug} – Return data about how many times that link was visited, timestamps of visits, etc.
- The exact shape of the data is up to you. An example response might be:
```json
[
  {
    "slug": "abcd123",
    "long_url": "https://www.example.com/...",
    "visits": 42,
    "last_visit": "2025-12-01T13:00:00Z"
  }
]
```

## Additional Consideration
Think about these things as you are designing your implementation

### Database
- You must use a relational database (e.g., PostgreSQL or MySQL).
- Show how you manage schema or migrations.
- Consider indexing. This service could potentially handle a high volume of requests.

### Scalability
- The service may receive bursts of traffic or a large backlog of links.
- Show a concurrency strategy (e.g., how FastAPI handles multiple requests).
- No need for a fully distributed system, but demonstrate an approach that wouldn’t deadlock or degrade severely under moderate scale.

### Deployment
- Provide a Dockerfile and instructions (or a docker-compose.yml) to run the service.
- If possible, host it somewhere we can test (like a small VM or container).

### Testing
- Include a basic test suite (e.g., pytest) verifying endpoints.
- Unit tests for core logic + an integration test or two for the overall API are ideal.

### Code Quality & Documentation
- Clean, logical Python code with appropriate docstrings and function naming.
- A short README.md explaining how to install, run, and test your project.
- Good structure: for instance, separate modules for models, routes, and “business logic” or “services.”


## Evaluation Criteria

### We’ll be reviewing:
- API correctness: Does the service meet the requirements?
- Database design: Are schemas, indices, and queries well thought-out?
- Performance: Any obviously inefficient design choices (e.g., storing massive data in memory, no indexing)?
- Code clarity: Is the Python code idiomatic, maintainable, and logically separated?
- Deployment: Can we hit the API?

### Deliverables
Please clone the provided Git repository, add your code, then push your changes or submit a link to your repository:

- Source code in Python + FastAPI.
- App setup (Dockerfile / docker-compose / sh script).
- README.md with:
  - Setup instructions
  - How to run tests
  - Any design notes or trade-offs you made

In the following interview we will be spinning up your service and running some locust tests on it.

Good luck and have fun.
