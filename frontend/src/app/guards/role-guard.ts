import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { map, catchError, of } from 'rxjs';

import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route, state) => {

  const authService = inject(AuthService);
  const router = inject(Router);

  const allowedRoles = route.data['roles'] as string[] | undefined;

  // If a route has no role restriction,
  // allow any authenticated user.
  if (!allowedRoles || allowedRoles.length === 0) {
    return true;
  }

  return authService.getMe().pipe(

    map((user) => {

      const userRole = String(user.role_name || '')
        .trim()
        .toUpperCase()
        .replace(/ /g, '_');

      const normalizedRoles = allowedRoles.map(role =>
        String(role)
          .trim()
          .toUpperCase()
          .replace(/ /g, '_')
      );

      if (normalizedRoles.includes(userRole)) {
        return true;
      }

      router.navigate(['/dashboard']);
      return false;
    }),

    catchError(() => {
      router.navigate(['/login']);
      return of(false);
    })
  );
};