# issues-to-csv

Fetches all issues from a SonarQube instance and exports them to a timestamped CSV file.

## Requirements

- Python 3.6+
- No external dependencies — uses stdlib only

## Setup

1. Copy the sample config and fill in your details:

   ```
   cp endpoint.json.sample endpoint.json
   ```

2. Edit `endpoint.json`:

   ```json
   {
     "endpoint_url": "https://your-sonarqube-host.example.com",
     "endpoint_token": "your_sonarqube_token_here"
   }
   ```

   - `endpoint_url` — base URL of your SonarQube instance (no trailing slash)
   - `endpoint_token` — a SonarQube user token with at least Browse permission

## Usage

```
python3 fetch_issues.py
```

The script will page through all results and write a single CSV to the `outputs/` directory named after the UTC timestamp of the run (e.g. `outputs/20260316T142300Z.csv`).

Progress is printed to stdout:

```
Fetching page 1...
  Got 500 issues (total so far: 500 / 1243)
Fetching page 2...
  Got 500 issues (total so far: 1000 / 1243)
Fetching page 3...
  Got 243 issues (total so far: 1243 / 1243)

Done. 1243 issues written to outputs/20260316T142300Z.csv
```

## Output format

Each CSV contains a header row followed by one row per issue:

| Column | Description |
|---|---|
| `project` | SonarQube project key |
| `rule` | Rule key that triggered the issue |
| `severity` | Severity level (BLOCKER, CRITICAL, MAJOR, MINOR, INFO) |
| `author` | SCM author of the line where the issue was raised |
| `effort` | Remediation effort (e.g. `5min`) |
| `creationDate` | ISO 8601 timestamp when the issue was first detected |
| `updateDate` | ISO 8601 timestamp of the last update to the issue |

## Notes

- The API is queried with the maximum page size of 500 to minimise the number of requests.
- `endpoint.json` and the `outputs/` directory are excluded from version control via `.gitignore`.
