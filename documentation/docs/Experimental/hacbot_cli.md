---
sidebar_position: 2
---
# Hackbot CLI

## Step 1

Install the Gatling Gun CLI

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="pip" label="pip">

```bash
pip install hackbot
```

  </TabItem>
  <TabItem value="pip3" label="pip3">

```bash
pip3 install ggun
```

  </TabItem>
</Tabs>


## Step 2



Get a Gatling Gun API key from the [Gatling Gun website](https://ggun.com).

## Step 3

Set the `API_URL` environment variable to `http://34.89.77.42:8081` (Temporary)

```bash
export API_URL=http://34.89.77.42:8081
```

## Step 4

Run the Gatling Gun CLI on a foundry project. `ggun` expects a foundry project to be in the current directory, like below:

```text
example_foundry_project/
├── foundry.toml
├── lib/
│   └── forge-std
├── README.md
├── script/
│   └── Counter.s.sol
├── src/
│   └── Counter.sol
└── test/
    └── Counter.t.sol
```

```bash
$ ggun test
No files changed, compilation skipped

Ran 2 tests for test/Counter.t.sol:CounterTest
[PASS] testFuzz_SetNumber(uint256) (runs: 256, μ: 30474, ~: 31252)
[PASS] test_Increment() (gas: 31225)
Suite result: ok. 2 passed; 0 failed; 0 skipped; finished in 15.15ms (14.74ms CPU time)

Ran 1 test suite in 15.65ms (15.15ms CPU time): 2 tests passed, 0 failed, 0 skipped (2 total tests)
```
