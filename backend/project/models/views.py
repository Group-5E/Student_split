# --/ !!! >
# --[ SQL view definitions, built on top of the core tables
# --[ Call create_views(engine) after db.create_all(engine)

# --[ How much each student owes each other within a household
# --[ Excludes the payer's own split row (user_id != paid_by_id)
from sqlalchemy import text
DEBT_SUMMARY_VIEW = """
CREATE VIEW IF NOT EXISTS v_debt_summary AS
SELECT
    es.user_id AS debtor_id,
    e.paid_by_id AS creditor_id,
    e.household_id,
    SUM(CASE WHEN NOT es.is_settled THEN es.amount_owed ELSE 0 END) AS amount_outstanding,
    SUM(CASE WHEN es.is_settled THEN es.amount_owed ELSE 0 END) AS total_settled,
    SUM(es.amount_owed) AS total_owed
FROM expense_splits es
JOIN expenses e ON e.id = es.expense_id
WHERE e.is_deleted = 0
  AND es.user_id != e.paid_by_id
GROUP BY es.user_id, e.paid_by_id, e.household_id;
"""

# --[ Aggregated expense and balance stats per household
HOUSEHOLD_STATS_VIEW = """
CREATE VIEW IF NOT EXISTS v_household_stats AS
SELECT
    h.id AS household_id,
    h.name AS household_name,
    COUNT(DISTINCT e.id) AS total_expenses,
    COALESCE(SUM(e.amount), 0) AS total_spent,
    COALESCE(SUM(CASE WHEN es.is_settled = 1 THEN es.amount_owed END), 0) AS total_settled,
    COALESCE(SUM(CASE WHEN es.is_settled = 0 THEN es.amount_owed END), 0) AS total_outstanding,
    COUNT(DISTINCT hm.user_id) AS member_count
FROM households h
LEFT JOIN expenses e ON e.household_id = h.id AND e.is_deleted = 0
LEFT JOIN expense_splits es ON es.expense_id = e.id
LEFT JOIN household_members hm ON hm.household_id = h.id AND hm.is_active = 1
GROUP BY h.id, h.name;
"""

# --[ Per user summary of expenses paid, splits involved in, and payments made
USER_ACTIVITY_VIEW = """
CREATE VIEW IF NOT EXISTS v_user_activity AS
SELECT
    u.id AS user_id,
    u.username,
    COUNT(DISTINCT e.id) AS expenses_paid_count,
    COALESCE(SUM(e.amount), 0) AS total_paid_out,
    COUNT(DISTINCT es.id) AS splits_involved_in,
    COALESCE(SUM(es.amount_owed), 0) AS total_owed_across_splits,
    COUNT(DISTINCT p.id) AS payments_made,
    u.last_active_at
FROM users u
LEFT JOIN expenses e ON e.paid_by_id = u.id AND e.is_deleted = 0
LEFT JOIN expense_splits es ON es.user_id = u.id
LEFT JOIN payments p ON p.payer_id = u.id
GROUP BY u.id, u.username, u.last_active_at;
"""

# --[ Net balance per student per household
# --[ Positive = owed money, Negative = owes money
USER_BALANCE_VIEW = """
CREATE VIEW IF NOT EXISTS v_user_balance AS
SELECT
    hm.user_id,
    hm.household_id,
    COALESCE(paid.total_paid, 0) AS total_paid,
    COALESCE(owed.total_owed, 0) AS total_owed,
    COALESCE(paid.total_paid, 0) - COALESCE(owed.total_owed, 0) AS net_balance
FROM household_members hm
LEFT JOIN (
    SELECT paid_by_id AS user_id, household_id, SUM(amount) AS total_paid
    FROM expenses WHERE is_deleted = 0
    GROUP BY paid_by_id, household_id
) paid ON paid.user_id = hm.user_id AND paid.household_id = hm.household_id
LEFT JOIN (
    SELECT es.user_id, e.household_id, SUM(es.amount_owed) AS total_owed
    FROM expense_splits es
    JOIN expenses e ON e.id = es.expense_id AND e.is_deleted = 0
    WHERE es.user_id != e.paid_by_id
    GROUP BY es.user_id, e.household_id
) owed ON owed.user_id = hm.user_id AND owed.household_id = hm.household_id
WHERE hm.is_active = 1;
"""

# --[ Executes all view DDL against the database
# --[ Must be called after Base.metadata.create_all(engine)
# --[ Safe to re-run as all views use CREATE VIEW IF NOT EXISTS
def create_views(engine):
    with engine.connect() as conn:
        for view_sql in [DEBT_SUMMARY_VIEW, HOUSEHOLD_STATS_VIEW, USER_ACTIVITY_VIEW, USER_BALANCE_VIEW]:
            conn.execute(text(view_sql))
        conn.commit()
