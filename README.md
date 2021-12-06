# Introduction

This directory contains the test framework for the *Enable Project
Level Custom Fields* feature for CxFlow.

# Test Cases

The following test cases have been implemented.

## Custom Fields Provided on the Command Line

CxFlow is launched specifying two random scan-level custom fields
using the `--scan-custom-field` command line option.

## Custom Fields Provided Using Config-As-Code

Two random scan-level custom fields are added to the `cx.config` file
before launching CxFlow.

## No Custo Fields Provided

CxFlow is launched with no scan-level custom fields specified.

# Configuration

The test framework expects there to be a file names `config.yml` in
the current directory. This file, which is not tracked in version
control, contains the CxSAST and Jira credentials as well as the base
and test versions of CxFlow.

Here is an example `config.yml` file:

```
cx-flow:
  version: 1.6.27

checkmarx:
  api-version: "1.2"
  base-url: http://EC2AMAZ-3JBTK7R
  username: cxsastuser
  password: secret
```

**Note:** If running the tests on an older version of CxSAST, make
  sure to update the `api-version` accordingly.
