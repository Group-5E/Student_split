### WHAT STAYED THE SAME
* Student actor and email provider (same roles and responsibilities)
* Frontend is still react
* Same structure (frontend, API, database)

### WHAT IS DIFFERENT
* Express (node.js) is now Flask (Python)
* PostgreSQL is now SQLite
* memberships table is now household_members, and now has role and timestamps
* Two new tables added, payments, expense_splits
* A views layer added on top of database
* flask-login added for auth

### CONCLUSION
* Components have changed
* Relationships are mostly the same
* Architecture is unchanged
* No components merged
* More specific data entries
