### Sports Management

Foundation app for school sports operations in Frappe / ERPNext.

Implemented in this pass:

- app hooks and install-time role/workspace setup
- core sports doctypes for settings, sports, seasons, teams, athletes, and coaches
- basic website helpers and public `/sports` landing page

Next phases should add team membership, fixtures, results, training, attendance, and dashboards.

### Public profile details

Coach, Athlete, and Sports Team forms include **Additional Profile Details** and
**Website Display Options**. Enter the relevant information and tick its
**Show … on Website** checkbox to include it on the published profile. Empty
fields and unticked details are omitted. New characteristics are off by default;
details that were already public retain their existing display settings.

Athlete and team photos must use public images when their display option is enabled.
Links to coaches, captains, and teams are shown only for published linked profiles.
The sports templates share a full-height page layout that places the footer at
the bottom of short pages and below the content of longer pages.
