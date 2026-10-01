import {
  Component,
  OnInit,
  inject,
  ChangeDetectorRef
} from '@angular/core';

import { FormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';

import { PurchaseOrderService } from '../../../../services/purchase-order.service';

import {
  DeliveryService,
  DeliveryCreate
} from '../../../../services/delivery.service';

@Component({
  selector: 'app-delivery-tracking',
  standalone: true,

  imports: [
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatButtonModule,
    MatTableModule,
    MatChipsModule
  ],

  templateUrl: './delivery-tracking.html',
  styleUrl: './delivery-tracking.css'
})
export class DeliveryTracking implements OnInit {

  purchaseOrders: any[] = [];
  deliveries: any[] = [];

  displayedColumns: string[] = [
    'po',
    'vendor',
    'tracking',
    'carrier',
    'expected',
    'status',
    'actions'
  ];

  selectedPoId = '';

  trackingNumber = '';
  carrier = '';
  expectedDate = '';
  remarks = '';

  successMessage = '';
  errorMessage = '';

  private purchaseOrderService =
    inject(PurchaseOrderService);

  private deliveryService =
    inject(DeliveryService);

  private cdr =
    inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.loadPurchaseOrders();
    this.loadDeliveries();
  }

  loadPurchaseOrders(): void {

    this.purchaseOrderService.getPurchaseOrders().subscribe({

      next: (orders) => {

        this.purchaseOrders = orders || [];

        this.cdr.markForCheck();
      },

      error: (error) => {

        console.error(
          'Unable to load purchase orders:',
          error
        );

        this.purchaseOrders = [];

        this.errorMessage =
          'Unable to load purchase orders.';

        this.cdr.markForCheck();
      }
    });
  }

  loadDeliveries(): void {

    this.deliveryService.getDeliveries().subscribe({

      next: (deliveries) => {

        this.deliveries = deliveries || [];

        console.log(
          'Delivery records:',
          this.deliveries
        );

        this.cdr.markForCheck();
      },

      error: (error) => {

        console.error(
          'Unable to load deliveries:',
          error
        );

        this.deliveries = [];

        this.cdr.markForCheck();
      }
    });
  }

  createDelivery(): void {

    this.successMessage = '';
    this.errorMessage = '';

    if (!this.selectedPoId) {

      this.errorMessage =
        'Please select a purchase order.';

      return;
    }

    const selectedPo =
      this.purchaseOrders.find(
        po => po.po_id === this.selectedPoId
      );

    const deliveryData: DeliveryCreate = {

      po_id: this.selectedPoId,

      tracking_number:
        this.trackingNumber.trim() || undefined,

      carrier:
        this.carrier.trim() || undefined,

      expected_date:
        this.expectedDate ||
        selectedPo?.expected_delivery_date ||
        undefined,

      remarks:
        this.remarks.trim() || undefined
    };

    this.deliveryService
      .createDelivery(deliveryData)
      .subscribe({

        next: (response) => {

          console.log(
            'Delivery created:',
            response
          );

          this.successMessage =
            'Delivery tracking record created successfully.';

          this.resetForm();

          this.loadDeliveries();
        },

        error: (error) => {

          console.error(
            'Unable to create delivery:',
            error
          );

          this.errorMessage =
            error?.error?.detail ||
            'Unable to create delivery tracking record.';

          this.cdr.markForCheck();
        }
      });
  }

  dispatchDelivery(deliveryId: string): void {

    this.successMessage = '';
    this.errorMessage = '';

    this.deliveryService
      .dispatchDelivery(deliveryId)
      .subscribe({

        next: (response) => {

          console.log(
            'Delivery dispatched:',
            response
          );

          this.successMessage =
            'Shipment dispatched successfully.';

          this.loadDeliveries();
        },

        error: (error) => {

          console.error(
            'Unable to dispatch delivery:',
            error
          );

          this.errorMessage =
            error?.error?.detail ||
            'Unable to dispatch shipment.';

          this.cdr.markForCheck();
        }
      });
  }

  markDelivered(deliveryId: string): void {

    this.successMessage = '';
    this.errorMessage = '';

    this.deliveryService
      .markDelivered(deliveryId)
      .subscribe({

        next: (response) => {

          console.log(
            'Delivery marked as delivered:',
            response
          );

          this.successMessage =
            'Shipment marked as delivered.';

          this.loadDeliveries();
        },

        error: (error) => {

          console.error(
            'Unable to mark delivery as delivered:',
            error
          );

          this.errorMessage =
            error?.error?.detail ||
            'Unable to mark shipment as delivered.';

          this.cdr.markForCheck();
        }
      });
  }

  markDelayed(deliveryId: string): void {

    this.successMessage = '';
    this.errorMessage = '';

    this.deliveryService
      .markDelayed(
        deliveryId,
        undefined,
        'Shipment delayed for performance testing.'
      )
      .subscribe({

        next: (response) => {

          console.log(
            'Delivery marked as delayed:',
            response
          );

          this.successMessage =
            'Shipment marked as delayed.';

          this.loadDeliveries();
        },

        error: (error) => {

          console.error(
            'Unable to mark delivery as delayed:',
            error
          );

          this.errorMessage =
            error?.error?.detail ||
            'Unable to mark shipment as delayed.';

          this.cdr.markForCheck();
        }
      });
  }

  private resetForm(): void {

    this.selectedPoId = '';

    this.trackingNumber = '';

    this.carrier = '';

    this.expectedDate = '';

    this.remarks = '';

    this.cdr.markForCheck();
  }

  getStatusClass(status: string): string {

    return String(status || '')
      .toLowerCase()
      .replace(/_/g, '-');
  }
}