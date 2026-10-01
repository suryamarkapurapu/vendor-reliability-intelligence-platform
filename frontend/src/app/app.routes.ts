import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { VendorManagement } from './pages/vendor-management/vendor-management';
import { VendorPerformance } from './pages/vendor-performance/vendor-performance';
import { ProcurementManagement } from './pages/procurement-management/procurement-management';
import { PurchaseOrders } from './pages/purchase-orders/purchase-orders';
import { ContractManagement } from './pages/contract-management/contract-management';
import { Communication } from './pages/communication/communication';
import { Analytics } from './pages/analytics/analytics';
import { Reports } from './pages/reports/reports';
import { Settings } from './pages/settings/settings';
import { authGuard } from './guards/auth-guard';
import { Register } from './pages/auth/register/register';
import { ForgotPassword } from './pages/auth/forgot-password/forgot-password';
import { ResetPassword } from './pages/auth/reset-password/reset-password';
import { VendorIssues } from './pages/vendor-issues/vendor-issues';
import { roleGuard } from './guards/role-guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    component: Login
  },
  {
    path: 'register',
    component: Register
  },
  {
    path: 'forgot-password',
    component: ForgotPassword
  },
  {
    path: 'reset-password',
    component: ResetPassword
  },
  {
    path: 'dashboard',
    component: Dashboard,
    canActivate: [authGuard]
  },
 {
  path: 'vendor-management',
  component: VendorManagement,
  canActivate: [authGuard, roleGuard],
  data: {
    roles: [
      'ADMIN',
      'ADMINISTRATOR',
      'PROCUREMENT_MANAGER'
    ]
  }
},
{
  path: 'vendor-performance',
  component: VendorPerformance,
  canActivate: [authGuard, roleGuard],
  data: {
    roles: [
      'ADMIN',
      'ADMINISTRATOR',
      'PROCUREMENT_MANAGER',
      'SUPPLY_CHAIN_MANAGER',
      'FINANCE_OFFICER',
      'LOGISTICS_MANAGER',
      'AUDITOR'
    ]
  }
},
  {
  path: 'vendor-issues',
  component: VendorIssues,
  canActivate: [authGuard]
},
{
  path: 'procurement-management',
  component: ProcurementManagement,
  canActivate: [authGuard, roleGuard],
  data: {
    roles: [
      'ADMIN',
      'ADMINISTRATOR',
      'PROCUREMENT_MANAGER'
    ]
  }
},
{
  path: 'purchase-orders',
  component: PurchaseOrders,
  canActivate: [authGuard, roleGuard],
  data: {
    roles: [
      'ADMIN',
      'ADMINISTRATOR',
      'PROCUREMENT_MANAGER'
    ]
  }
},
  {
    path: 'contract-management',
    component: ContractManagement,
    canActivate: [authGuard]
  },
{
  path: 'analytics',
  component: Analytics,
  canActivate: [authGuard, roleGuard],
  data: {
    roles: [
      'ADMIN',
      'ADMINISTRATOR',
      'PROCUREMENT_MANAGER',
      'SUPPLY_CHAIN_MANAGER',
      'FINANCE_OFFICER',
      'LOGISTICS_MANAGER',
      'AUDITOR'
    ]
  }
},
  {
    path: 'communication',
    component: Communication,
    canActivate: [authGuard]
  },
{
  path: 'reports',
  component: Reports,
  canActivate: [authGuard, roleGuard],
  data: {
    roles: [
      'ADMIN',
      'ADMINISTRATOR',
      'PROCUREMENT_MANAGER',
      'SUPPLY_CHAIN_MANAGER',
      'FINANCE_OFFICER',
      'LOGISTICS_MANAGER',
      'AUDITOR'
    ]
  }
},
  {
    path: 'settings',
    component: Settings,
    canActivate: [authGuard]
  },
  {
    path: '**',
    redirectTo: 'login'
  }
];
