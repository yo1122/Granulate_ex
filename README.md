# Granulate_ex

# project status: Dev (poc)
# TODO:
* validate input
* add to constants - there should be no meaningful hard coded values in the code (if a typo does more than be displayed it's meaningful enough)
* replace printing to screen with logging ( & consider alerting on malicious activity)
* Configure WS connection with env vars instead of params for local debugging 
* Handle more errors & edge cases like concurrency issues ; reconnecting ; handle long server timeout
* Handle authentication properlly, started using "sessions" as first attempt to handle this. currently relevant code is just for show. 
* Handle SSL correctly (!!!! currently code in dev mode, not safe for production !!!)
* use "seen_by" to sent read ack (model prepared for this, didn't finish code)
* Create UI (not in exercise scope)
* Tests - unittests at least for each endpoint and case (success/fail/error) ; an end to end sanity check with some basic scenarios (not in exercise scope?)
