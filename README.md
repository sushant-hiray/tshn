tshn
====

Top Stories of Hacker News in last 24 hours!

Instructions
------------
Checkout `run.sh` for a sample bash script

Change the path to `scrape.py`

Now add a cron task as follows:

1. Open terminal and type `crontab -e`
2. Append the following line into the opened file:
   `*/15 * * * * <path to run.sh>`
3. Once the cron task is set right, the script will scrape front page of HN every 15 minutes and update the top stories data accordingly.
