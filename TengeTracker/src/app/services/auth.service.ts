import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export const API_URL = 'http://localhost:8000/api';

interface AuthResponse {
  token: string;
  username: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);

  private authRequest(endpoint: string, body: any): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${API_URL}/${endpoint}`, body)
      .pipe(tap(res => this.storeToken(res.token, res.username)));
  }

  register(data: { username: string; email: string; password: string }) {
    return this.authRequest('register/', data);
  }

  login(username: string, password: string) {
    return this.authRequest('login/', { username, password });
  }

  logout() {
    return this.http.post(`${API_URL}/logout/`, {}).pipe(
      tap(() => this.clear()) 
    );
  }

  me() {
    return this.http.get<{ id: number; username: string; email: string }>(`${API_URL}/me/`);
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('tt_token');
  }

  getUsername(): string {
    return localStorage.getItem('tt_username') ?? '';
  }

  private storeToken(token: string, username: string) {
    localStorage.setItem('tt_token', token);
    localStorage.setItem('tt_username', username);
  }

  private clear() {
    localStorage.removeItem('tt_token');
    localStorage.removeItem('tt_username');
  }
}