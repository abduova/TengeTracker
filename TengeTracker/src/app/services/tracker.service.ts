import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_URL } from './auth.service';
import {
  Balance,
  Category,
  SummaryRow,
  Transaction,
  TxFilters,
  Wallet,
} from '../models/models';

@Injectable({ providedIn: 'root' })
export class TrackerService {
  private http = inject(HttpClient);

  //Wallets
  listWallets(): Observable<Wallet[]> {
    return this.http.get<Wallet[]>(`${API_URL}/wallets/`);
  }
  createWallet(w: Wallet): Observable<Wallet> {
    return this.http.post<Wallet>(`${API_URL}/wallets/`, w);
  }
  updateWallet(id: number, w: Partial<Wallet>): Observable<Wallet> {
    return this.http.patch<Wallet>(`${API_URL}/wallets/${id}/`, w);
  }
  deleteWallet(id: number): Observable<unknown> {
    return this.http.delete(`${API_URL}/wallets/${id}/`);
  }

  //Categories
  listCategories(type?: 'income' | 'expense'): Observable<Category[]> {
    let params = new HttpParams();
    if (type) params = params.set('type', type);
    return this.http.get<Category[]>(`${API_URL}/categories/`, { params });
  }
  createCategory(c: Category): Observable<Category> {
    return this.http.post<Category>(`${API_URL}/categories/`, c);
  }
  updateCategory(id: number, c: Partial<Category>): Observable<Category> {
    return this.http.patch<Category>(`${API_URL}/categories/${id}/`, c);
  }
  deleteCategory(id: number): Observable<unknown> {
    return this.http.delete(`${API_URL}/categories/${id}/`);
  }

  //Transactions
  listTransactions(filters: TxFilters = {}): Observable<Transaction[]> {
    let params = new HttpParams();
    for (const [k, v] of Object.entries(filters)) {
      if (v !== undefined && v !== null && v !== '') {
        params = params.set(k, String(v));
      }
    }
    return this.http.get<Transaction[]>(`${API_URL}/transactions/`, { params });
  }
  createTransaction(t: Transaction): Observable<Transaction> {
    return this.http.post<Transaction>(`${API_URL}/transactions/create/`, t);
  }
  updateTransaction(id: number, t: Partial<Transaction>): Observable<Transaction> {
    return this.http.patch<Transaction>(`${API_URL}/transactions/update/${id}/`, t);
  }
  deleteTransaction(id: number): Observable<unknown> {
    return this.http.delete(`${API_URL}/transactions/delete/${id}/`);
  }

  //Summaries
  getBalance(): Observable<Balance> {
    return this.http.get<Balance>(`${API_URL}/transactions/balance/`);
  }
  getCategorySummary(type?: 'income' | 'expense'): Observable<SummaryRow[]> {
    if (type === 'income') return this.getIncomeSummary();
    return this.http.get<SummaryRow[]>(`${API_URL}/transactions/summary/`);
  }
  getIncomeSummary(): Observable<SummaryRow[]> {
    return this.http.get<SummaryRow[]>(`${API_URL}/transactions/income-summary/`);
  }
  getWalletSummary(): Observable<SummaryRow[]> {
    return this.http.get<SummaryRow[]>(`${API_URL}/transactions/wallet-summary/`);
  }
}
