export interface User {
  id: number;
  username: string;
  email?: string;
}

export interface Wallet {
  id?: number;
  name: string;
  balance: number;
  icon?: string;
  color?: string;
}

export interface Category {
  id?: number;
  name: string;
  type: 'income' | 'expense';
  icon?: string;
  color?: string;
}

export interface Transaction {
  id?: number;
  amount: number;
  type: 'income' | 'expense';
  wallet: number;
  category: number;
  description?: string | null;
  created_at?: string;
  wallet_name?: string;
  category_name?: string;
  category_icon?: string;
  category_color?: string;
}

export interface Balance {
  income: number;
  expense: number;
  balance: number;
}

export interface SummaryRow {
  category__name?: string;
  category__icon?: string;
  category__color?: string;
  wallet__name?: string;
  wallet__icon?: string;
  wallet__color?: string;
  total: number;
}

export interface TxFilters {
  category?: string;
  wallet?: string;
  type?: 'income' | 'expense' | '';
  start_date?: string;
  end_date?: string;
  min_amount?: number | null;
  max_amount?: number | null;
  order?: 'asc' | 'desc' | '';
}

//icons
export const ICON_CATALOG: { key: string; label: string; file: string }[] = [
  { key: 'income',        label: 'Income',         file: 'income.png' },
  { key: 'income2',       label: 'Salary',         file: 'income2.png' },
  { key: 'cash',          label: 'Cash',           file: 'cash.png' },
  { key: 'card',          label: 'Card',           file: 'card.png' },
  { key: 'property',      label: 'Property',       file: 'property.png' },
  { key: 'grossories',    label: 'Groceries',      file: 'grossories.png' },
  { key: 'food',          label: 'Food',           file: 'food.png' },
  { key: 'entertainment', label: 'Entertainment',  file: 'entertainment.png' },
  { key: 'shopping',      label: 'Shopping',       file: 'shopping.png' },
  { key: 'network',       label: 'Internet/Mobile',file: 'network.png' },
];

export function iconPath(key?: string): string {
  const found = ICON_CATALOG.find((i) => i.key === key);
  return found ? `icons/${found.file}` : 'icons/income.png';
}
