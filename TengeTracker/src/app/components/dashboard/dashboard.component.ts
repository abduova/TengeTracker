import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TrackerService } from '../../services/tracker.service';
import {
  Balance,
  Category,
  ICON_CATALOG,
  SummaryRow,
  Transaction,
  Wallet,
  iconPath,
} from '../../models/models';

type ModalKind = 'none' | 'wallet' | 'income' | 'expense' | 'tx';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  private auth = inject(AuthService);
  private api = inject(TrackerService);
  private router = inject(Router);

  username = this.auth.getUsername();
  icons = ICON_CATALOG;
  iconPath = iconPath;

  wallets = signal<Wallet[]>([]);
  incomeCats = signal<Category[]>([]);
  expenseCats = signal<Category[]>([]);
  walletSummary = signal<SummaryRow[]>([]);
  incomeSummary = signal<SummaryRow[]>([]);
  expenseSummary = signal<SummaryRow[]>([]);
  balance = signal<Balance>({ income: 0, expense: 0, balance: 0 });

  loading = signal(true);
  modal = signal<ModalKind>('none');

  //Wallet
  walletName = '';
  walletBalance = 0;
  walletIcon = 'cash';
  walletColor = '#3b82f6';

  //Category
  categoryName = '';
  categoryIcon = 'income';
  categoryColor = '#22c55e';
  categoryType: 'income' | 'expense' = 'income';

  // Transaction
  txType: 'income' | 'expense' = 'expense';
  txAmount: number | null = null;
  txWallet: number | null = null;
  txCategory: number | null = null;
  txDescription = '';
  txError = signal('');

  totalBalance = computed(() =>
    this.wallets().reduce((sum, w) => sum + (Number(w.balance) || 0), 0),
  );

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.api.listWallets().subscribe({
      next: (ws) => this.wallets.set(ws),
      error: () => this.wallets.set([]),
    });
    this.api.listCategories('income').subscribe({
      next: (c) => this.incomeCats.set(c),
      error: () => this.incomeCats.set([]),
    });
    this.api.listCategories('expense').subscribe({
      next: (c) => this.expenseCats.set(c),
      error: () => this.expenseCats.set([]),
    });
    this.api.getWalletSummary().subscribe({
      next: (s) => this.walletSummary.set(s),
      error: () => this.walletSummary.set([]),
    });
    this.api.getIncomeSummary().subscribe({
      next: (s) => this.incomeSummary.set(s),
      error: () => this.incomeSummary.set([]),
    });
    this.api.getCategorySummary('expense').subscribe({
      next: (s) => this.expenseSummary.set(s),
      error: () => this.expenseSummary.set([]),
    });
    this.api.getBalance().subscribe({
      next: (b) => {
        this.balance.set(b);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  openWallet(): void {
    this.walletName = '';
    this.walletBalance = 0;
    this.walletIcon = 'cash';
    this.walletColor = '#3b82f6';
    this.modal.set('wallet');
  }
  openIncomeCat(): void {
    this.categoryName = '';
    this.categoryIcon = 'income';
    this.categoryColor = '#22c55e';
    this.categoryType = 'income';
    this.modal.set('income');
  }
  openExpenseCat(): void {
    this.categoryName = '';
    this.categoryIcon = 'grossories';
    this.categoryColor = '#ef4444';
    this.categoryType = 'expense';
    this.modal.set('expense');
  }
  openTx(type: 'income' | 'expense'): void {
    this.txType = type;
    this.txAmount = null;
    this.txDescription = '';
    this.txError.set('');
    this.txWallet = this.wallets()[0]?.id ?? null;
    const cats = type === 'income' ? this.incomeCats() : this.expenseCats();
    this.txCategory = cats[0]?.id ?? null;
    this.modal.set('tx');
  }
  closeModal(): void {
    this.modal.set('none');
  }

  saveWallet(): void {
    if (!this.walletName.trim()) return;
    this.api
      .createWallet({
        name: this.walletName.trim(),
        balance: Number(this.walletBalance) || 0,
        icon: this.walletIcon,
        color: this.walletColor,
      })
      .subscribe(() => {
        this.closeModal();
        this.reload();
      });
  }

  saveCategory(): void {
    if (!this.categoryName.trim()) return;
    this.api
      .createCategory({
        name: this.categoryName.trim(),
        type: this.categoryType,
        icon: this.categoryIcon,
        color: this.categoryColor,
      })
      .subscribe(() => {
        this.closeModal();
        this.reload();
      });
  }

  saveTx(): void {
    this.txError.set('');
    if (!this.txAmount || this.txAmount <= 0) {
      this.txError.set('Amount must be greater than 0.');
      return;
    }
    if (!this.txWallet) {
      this.txError.set('Please select a wallet.');
      return;
    }
    if (!this.txCategory) {
      this.txError.set('Please select a category.');
      return;
    }
    const payload: Transaction = {
      amount: Number(this.txAmount),
      type: this.txType,
      wallet: this.txWallet,
      category: this.txCategory,
      description: this.txDescription || null,
    };
    this.api.createTransaction(payload).subscribe({
      next: () => {
        this.closeModal();
        this.reload();
      },
      error: (err) => {
        const data = err?.error || {};
        const firstKey = Object.keys(data)[0];
        let msg = 'Failed to save transaction';
        if (firstKey) {
          const val = data[firstKey];
          msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : String(val);
        }
        this.txError.set(msg);
      },
    });
  }

  deleteWallet(w: Wallet): void {
  if (!w.id) return;

  if (!confirm(`Delete wallet "${w.name}"?`)) return;

  this.api.deleteWallet(w.id).subscribe({
    next: () => {
      console.log('DELETE OK');
      this.reload();
    },
    error: (err) => {
      console.error('DELETE FAILED FULL ERROR:', err);
      console.error('STATUS:', err.status);
      console.error('BODY:', err.error);
    },
  });
}

  deleteIncomeCat(c: Category): void {
    if (!c.id) return;
    if (!confirm(`Delete category "${c.name}"?`)) return;
    this.api.deleteCategory(c.id).subscribe(() => this.reload());
  }

  deleteExpenseCat(c: Category): void {
    if (!c.id) return;
    if (!confirm(`Delete category "${c.name}"?`)) return;
    this.api.deleteCategory(c.id).subscribe(() => this.reload());
  }

  findIncomeTotal(name?: string): number {
    const row = this.incomeSummary().find((r) => r.category__name === name);
    return row?.total ?? 0;
  }
  findExpenseTotal(name?: string): number {
    const row = this.expenseSummary().find((r) => r.category__name === name);
    return row?.total ?? 0;
  }

  logout(): void {
    this.auth.logout().subscribe({
      next: () => this.router.navigate(['/login']),
      error: () => this.router.navigate(['/login']),
    });
  }
}
