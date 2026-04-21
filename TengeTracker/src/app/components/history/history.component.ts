import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TrackerService } from '../../services/tracker.service';
import {
  Category,
  Transaction,
  TxFilters,
  Wallet,
  iconPath,
} from '../../models/models';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './history.component.html',
  styleUrl: './history.component.css',
})
export class HistoryComponent implements OnInit {
  private auth = inject(AuthService);
  private api = inject(TrackerService);
  private router = inject(Router);

  username = this.auth.getUsername();
  iconPath = iconPath;

  wallets = signal<Wallet[]>([]);
  categories = signal<Category[]>([]);
  transactions = signal<Transaction[]>([]);
  loading = signal(false);

  filters: TxFilters = {
    category: '',
    wallet: '',
    type: '',
    start_date: '',
    end_date: '',
    min_amount: null,
    max_amount: null,
    order: 'desc',
  };

  ngOnInit(): void {
    this.api.listWallets().subscribe({
      next: (ws) => this.wallets.set(ws),
      error: () => this.wallets.set([]),
    });
    this.api.listCategories().subscribe({
      next: (cs) => this.categories.set(cs),
      error: () => this.categories.set([]),
    });
    this.search();
  }

  search(): void {
    this.loading.set(true);
    const cleaned: TxFilters = {};
    for (const [k, v] of Object.entries(this.filters)) {
      if (v !== '' && v !== null && v !== undefined) {
        (cleaned as any)[k] = v;
      }
    }
    this.api.listTransactions(cleaned).subscribe({
      next: (ts) => {
        this.transactions.set(ts);
        this.loading.set(false);
      },
      error: () => {
        this.transactions.set([]);
        this.loading.set(false);
      },
    });
  }

  reset(): void {
    this.filters = {
      category: '',
      wallet: '',
      type: '',
      start_date: '',
      end_date: '',
      min_amount: null,
      max_amount: null,
      order: 'desc',
    };
    this.search();
  }

  deleteTx(t: Transaction): void {
    if (!t.id) return;
    if (!confirm('Delete this transaction?')) return;
    this.api.deleteTransaction(t.id).subscribe(() => this.search());
  }

  totalIncome(): number {
    return this.transactions()
      .filter((t) => t.type === 'income')
      .reduce((sum, t) => sum + Number(t.amount), 0);
  }
  totalExpense(): number {
    return this.transactions()
      .filter((t) => t.type === 'expense')
      .reduce((sum, t) => sum + Number(t.amount), 0);
  }

  logout(): void {
    this.auth.logout().subscribe({
      next: () => this.router.navigate(['/login']),
      error: () => this.router.navigate(['/login']),
    });
  }
}
