This folder is where the example GitHub Action writes `tenders.csv`.

The workflow is `.github/workflows/daily-tenders.example.yml`. It runs only
when someone starts it by hand (`workflow_dispatch`). It is not on a
schedule, so the repository does not call Contracts Finder or Find a Tender
every day on its own.

There is no sample CSV here yet. After a manual run, the action commits
`tenders.csv` in this folder.
