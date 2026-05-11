export interface User {
  id: number;
  email: string;
  username: string;
  name: string;
  has_household: boolean;
  household_id: number | null;
  avatar: undefined;
}

export interface HouseholdMember {
  joined_at: string;
  name: string;
  role: string;
  user_id: number;
  username: string;
}

export interface Household {
  address: string;
  created_at: Date;
  id: number;
  member_count: number;
  name: string;
  role: string;
}

export type SplitType = "equal" | "percentage" | "fixed";

export interface Split {
  user_id: number;
  name: string;
  split_type: SplitType;
  amount: number;
}

export interface Expense {
  household_id: number;
  description: string;
  amount: number;
  expense_date: Date;
  splits: Split[];
}

export interface ExpenseResponse {
  amount: string;
  category: string;
  created_at: Date;
  description: string;
  expense_date: Date;
  household_id: number;
  id: number;
  notes: string | null;
  paid_by_id: number;
  paid_by_name: string;
  split_type: SplitType;
  splits: SplitResponse[];
}

export interface SplitResponse {
  amount_owed: string;
  id: number;
  is_settled: boolean;
  name: string;
  settled_at: Date | null;
  user_id: number;
  username: string;
}

export interface UpcomingPayment {
  splitId: number;
  expenseId: number;
  description: string;
  category: string;
  amount: number;
  owedTo: string;
  owedToId: number;
  expenseDate: Date;
}
