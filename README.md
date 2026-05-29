# Arryn Aid
Welcome to the Arryn Aid repo! This hosts the code used by the Discord bot in House Arryn.
## Features
**Reaction Roles:** Automated regional role assignment using message reactions.

**Event Logging:** Logs events sent in specific channels. Using the specified format, the event data is parsed, validated, and added to a SQLite database.
Note: invalid logs are deleted after 10s to prevent chat clutter. Valid logs get a checkmark.

If an event log is edited, the new log is checked against the old one and updated where necessary.

**Planned:** Entry message, auditing
## Event Log Format
Logs must follow this structure for the parser to validate them properly:
```text
Event Type: [Name]
Host: [@Mention]
Attendees: [@Mention1, @Mention2]
Proof: [Image/Link]
```
## Setup
1. Clone the repo.
2. Environment Variables: Create a .env file with:

    * `DISCORD_TOKEN`

    * `REACTION_ROLES_CHANNEL_ID` & `REACTION_ROLES_MESSAGE_ID`

    * `ARRYN_LOG_CHANNEL_ID`, `KNIGHTS_LOG_CHANNEL_ID`, `GUARDS_LOGS_CHANNEL_ID`, `CAVALRY_LOGS_CHANNEL_ID`
3. Create the `data/db.sqlite` file.
4. Install dependencies: `pip install -r requirements.txt` (preferably in a venv)
5. Run `python main.py` (preferably in a venv)
## Questions/Concerns?
DM MadTurtless on Discord.

### As high as honor
