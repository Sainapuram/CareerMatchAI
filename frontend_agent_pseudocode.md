
# CareerMatch AI — Frontend Development Agent

## Purpose
This AI agent is designed to replace my role in the CareerMatch AI capstone project. My responsibilities include frontend development, integrating teammates' modules, and testing the application.

## Inputs
- Project requirements and existing GitHub code
- O*NET occupation data
- Backend modules developed by teammates
- User feedback and reported errors

## Tools
- Python and Streamlit
- AI coding model
- GitHub
- Automated testing tools

## Pseudocode

```text
START CareerMatch_Developer_Agent

READ project requirements
ACCESS existing GitHub repository
ANALYZE application code

FOR each assigned task:

    IDENTIFY required frontend changes
    GENERATE or UPDATE Streamlit code

    IF required backend module is available:
        INTEGRATE module into frontend
    ELSE:
        RECORD missing dependency
        CONTINUE with other tasks

    RUN application tests

    IF tests fail:
        IDENTIFY errors
        ATTEMPT to fix errors
        RUN tests again

        IF errors remain:
            REPORT issue to team
            MARK task as blocked
            CONTINUE with next task

    IF tests pass:
        VERIFY application functionality
        SAVE changes to development branch

CHECK resume upload and skill extraction
CHECK career recommendations
CHECK Explore, Change, and Grow modes

GENERATE testing and progress report

END CareerMatch_Developer_Agent
```

## Outputs
- Updated Streamlit application
- Integrated application features
- Tested code on GitHub
- Error reports and progress summaries

## Evaluation
The agent is successful when the required features work correctly, backend integrations pass tests, errors are handled, and the application is easy to use.
