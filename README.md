# Introduction

This directory contains the test framework for the *Enable Project
Level Custom Fields* feature for CxFlow.

# Test Cases

The following test cases have been implemented.

## Project Does Not Exist

CxFlow is launched specifying a project that does not already
exist. The expectation is that the project is created and that its
custom fields are set to the provided values.

- Test using command line options
- Test using config-as-code

## Project Exists and Override Specified

CxFlow is launched specifying a project that already exists and that
the existing project configuration shoud be overridden. The
expectation is that the project's custom fields are set to the
provided values.

- Test using command line options
- Test using config-as-code

## Project Exists and Override Specified

CxFlow is launched specifying a project that already exists but it is
not specified that the existing project configuration shoud be
overridden. The expectation is that the project's custom fields are
not set to the provided values.

- Test using command line options
- Test using config-as-code

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
  base-url: http://EC2AMAZ-3JBTK7R
  username: cxsastuser
  password: secret
```

