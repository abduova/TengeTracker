import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink, CommonModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  username = '';
  email = '';
  password = '';
  confirm = '';

  loading = false;

  errors: any = {};
  generalError = '';

  submit(): void {
    this.errors = {};
    this.generalError = '';

    if (!this.username || !this.email || !this.password) {
      this.generalError = 'All fields are required';
      return;
    }

    if (this.password !== this.confirm) {
      this.generalError = 'Passwords do not match';
      return;
    }

    this.loading = true;

    this.auth.register({
      username: this.username,
      email: this.email,
      password: this.password,
    }).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },

      error: (err) => {
        console.log('REGISTER ERROR:', err);

        this.loading = false;

        const backendErrors = err?.error || {};

        this.errors = backendErrors;

        // show general error only if no field errors exist
        if (
          !backendErrors.username &&
          !backendErrors.email &&
          !backendErrors.password
        ) {
          this.generalError =
            backendErrors.detail ||
            backendErrors.message ||
            'Register Failed';
        }
      }
    });
  }
}