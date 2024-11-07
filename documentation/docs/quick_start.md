---
sidebar_position: 1
---
# Quick Start


:::warning
Hackbot CI is currently in beta. If you encounter any issues, please report them to us on [GitHub issues](https://github.com/GatlingX/hackbot_ci/issues).
:::

## Step 1: Get an API key

:::warning
Currently, you need to contact us to get an API key. Contact eito@gatlingx.com to get one.
:::

## Step 2: Install the Hackbot CLI

In your github repository, add the following to your `.github/workflows/hackbot.yml` file. Make sure to:
- replace the `<service address>` and `<service port>` with the address and port of the service you want to scan.
- replace the `username/repo` with the repository you want to create issues in.
- replace the `{{ secrets.YOUR_API_KEY }}` with your API key.
```yaml title=".github/workflows/hackbot.yml"
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
          address: <service address>
          port: <service port>
          api_key: ${{ secrets.YOUR_API_KEY }}
          output: "results.json"
          artifact: true
          generate_issues: true
          issues_repo: "username/repo"
        id: test-action

      - name: Print output
        run: |
          echo "Hack result: ${{ steps.test-action.outputs.results }}"  
```


