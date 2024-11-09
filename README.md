# Hackbot CI

This action is used to launch the Hackbot service and scan a contract for vurnabilities.

## Inputs

- `api_key`: The token to use to authenticate with the service (required).
- `output`: The output file to save the results to. Saved results are uploaded as an artifact if `artifact` is true. It can contain folder paths. (optional).
- `artifact`: Whether to upload the results as an artifact. (optional).
- `generate_issues`: Whether to generate issues with the results. It requires a `GITHUB_TOKEN` with `issues: write` permissions. (optional).
- `issues_repo`: The repository to generate issues in (username/repo). (required when `generate_issues` is true).

## Outputs

- `results`: The results of the hack in JSON format.


## Usage

To use this action in your GitHub workflow, follow these steps:

1. Create a new workflow file (e.g., `.github/workflows/hackbot-scan.yml`) in your repository.

2. Add the following content to the workflow file, adjusting the inputs as needed:
### Job section
Add the following permissions (e.g. after runs-on):
```yaml
permissions:
  contents: read
  issues: write
```
These permissions are required to read the repository and create issues in the repository. If you don't want to create issues, you can remove the `issues: write` permission. NOTE: Failures in the issue generation will not fail the workflow (i.e. the results and artifacts will still be created).

### Step section
```yaml
uses: GatlingX/hackbot-ci@v0.1.13
with:
  api_key: ${{ secrets.HACKBOT_API_KEY }}
  output: "results.json"
  artifact: true
  generate_issues: true
  issues_repo: "username/repo"
```
Option `api_key` is required and can be found in the Hackbot service settings.
Options `output` and `artifact` are optional. The `output` option instructs the action where to save the results. The `artifact` option instructs the action to upload the results as an artifact.
Option `generate_issues` is optional. When enabled, the action will create issues in the specified repository.
Option `issues_repo` is optional. It is used to specify the repository to create issues in and is required when `generate_issues` is `true`.

### Consequent steps
In concequent steps, the results can be accessed using the `results` output or the `output` file.
```yaml
${{ steps.test-action.outputs.results }}"
```


## Example

```yaml
name: Hackbot Scan Workflow

on:
  workflow_dispatch:

jobs:
  hackbot-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run Hackbot Scan
        uses: GatlingX/hackbot-ci@v0.1.13
        with:
          api_key: ${{ secrets.HACKBOT_API_KEY }}
          output: "results.json"
          artifact: true
          generate_issues: true
          issues_repo: "username/repo"
        id: test-action

      - name: Print output
        run: |
          echo "Hack result: ${{ steps.test-action.outputs.results }}"  
```
