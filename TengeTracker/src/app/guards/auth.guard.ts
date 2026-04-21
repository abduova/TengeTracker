import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = () => {
  const router = inject(Router);
  if (localStorage.getItem('tt_token')) return true;
  router.navigate(['/login']);
  return false;
};
