---
sidebar_position: 1
---

# Quick Start

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::warning
Hackbot CI is currently in beta. If you encounter any issues, please report them to us on [GitHub issues](https://github.com/GatlingX/hackbot_ci/issues).
:::

## ❗️ Requirements

- Your project must be hosted on GitHub.
- Your project must be a [Foundry project](https://book.getfoundry.sh/). (We will support Hardhat in the future.)
- You must have a `scope.txt` in your project root (recommended), or the `README.md` file needs to explicitly list the scope of the project. (More on this later.)

## Step 1: Create a `scope.txt` file in the project root

This `scope.txt` file on the root of your project is used to tell Hackbot which files to scan.

<Tabs>
  <TabItem value="scope_txt" label="Image">

![Scope File Example](scope_txt.png)

  </TabItem>
  <TabItem value="file_structure" label="Text">
```txt title="scope.txt"
./contracts/src/ccip/FeeQuoter.sol
./contracts/src/ccip/MultiAggregateRateLimiter.sol
./contracts/src/ccip/NonceManager.sol

...

./contracts/src/ccip/rmn/RMNHome.sol
./contracts/src/ccip/rmn/RMNRemote.sol
```

  </TabItem>
</Tabs>

For a file structure like this:

```
contracts/ 📁
├── src/ 📁
│   ├── ccip/ 📁
│   │   ├── 📄 FeeQuoter.sol
│   │   ├── 📄 MultiAggregateRateLimiter.sol
│   │   ├── 📄 NonceManager.sol
│   │   ...
│   ├── rmn/ 📁
│   │   ├── 📄 RMNHome.sol
│   │   ├── 📄 RMNRemote.sol
│   ...
📄 foundry.toml
📄 scope.txt
📄 README.md
```


## Step 2: Get an API key

:::warning
Currently, you need to contact us to get an API key. Contact eito@gatlingx.com to get one.
:::

## Step 3: Install the Hackbot CLI

### Option 1: Use the website-automated installation



### Option 2: Manually add the workflow to your repository

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


