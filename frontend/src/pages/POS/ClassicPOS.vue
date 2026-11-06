<template>
  <div>
    <OpenPOSShiftModal
      v-if="!isPosShiftOpen"
      v-model:open="isShiftOpenModalOpen"
    />

    <ClosePOSShiftModal v-model:open="isShiftCloseModalOpen" />

    <LoyaltyProgramModal
      v-model:open="isLoyaltyProgramModalOpen"
      :loyalty-points="loyaltyPoints"
      :loyalty-program="loyaltyProgram"
      @set-loyalty-points="(points) => emitEvent('setLoyaltyPoints', points)"
    />

    <BatchSelectionModal
      v-model:open="isBatchSelectionModalOpen"
      :item-code="selectedItemForBatch"
      @batch-selected="(batch) => emitEvent('batchSelected', batch)"
    />

    <SavedInvoiceModal
      v-model:open="isSavedInvoiceModalOpen"
      @selected-invoice-name="
        (invName) => emitEvent('selectedInvoiceName', invName)
      "
    />

    <CouponCodeModal
      v-model:open="isCouponCodeModalOpen"
      @apply-pricing-rule="emitEvent('applyPricingRule')"
      @set-coupons-count="(count) => emitEvent('setCouponsCount', count)"
    />

    <PriceListModal v-model:open="isPriceListModalOpen" />

    <ItemEnquiryModal
      v-model:open="isItemEnquiryModalOpen"
      :customer="sinvDoc?.party"
    />

    <PaymentModal
      v-model:open="isPaymentModalOpen"
      @set-paid-amount="(amount: Money) => emitEvent('setPaidAmount', amount)"
      @set-payment-method="
        (paymentMethod) => emitEvent('setPaymentMethod', paymentMethod)
      "
      @set-transfer-ref-no="(ref) => emitEvent('setTransferRefNo', ref)"
      @set-transfer-clearance-date="
        (date) => emitEvent('setTransferClearanceDate', date)
      "
      @create-transaction="
        (print, status) => emitEvent('createTransaction', print, status)
      "
    />

    <ReturnSalesInvoiceModal
      v-model:open="isReturnSalesInvoiceModalOpen"
      @selected-return-invoice="
        (value: any) => emitEvent('selectedReturnInvoice', value)
      "
    />

    <AlertModal
      v-model:open="isAlertModalOpen"
      @save-and-continue="(value: any) => emitEvent('saveAndContinue', value)"
    />

    <div
      class="h-[calc(100vh-var(--h-row-largest))] min-h-0 overflow-y-auto xl:overflow-hidden bg-surface-gray-1 grid grid-cols-1 xl:grid-cols-12 gap-2 p-4"
    >
      <div
        class="relative col-span-1 xl:col-span-5 min-h-[32rem] xl:min-h-0 overflow-hidden bg-surface-base border rounded-4 border-outline-gray-1"
      >
        <div
          class="flex h-full min-h-0 flex-col rounded-4 p-4 pb-14 col-span-5"
        >
          <div class="flex gap-x-2">
            <!-- Item Search -->
            <MultiLabelLink
              class="w-full"
              secondary-link="barcode"
              third-link="itemCode"
              :option-records="searchItems"
              :df="{
                label: t`Search Item (Name, Code, or Barcode)`,
                fieldtype: 'Link',
                fieldname: 'item',
                target: 'Item',
              }"
              :border="true"
              :value="itemSearchTerm"
              :show-clear-button="true"
              :close-on-enter="true"
              @search="(query: string) => emitEvent('handleItemSearch', query)"
              @enter="
                (value: string) => emitEvent('handleItemSearch', value, true)
              "
              @change="(item: string) => emitEvent('handleItemSearch', item)"
            />

            <Link
              v-if="fyo.singles.AccountingSettings?.enableitemGroup"
              :df="{
                label: t`Filter by Group`,
                fieldtype: 'Link',
                fieldname: 'itemGroup',
                target: 'ItemGroup',
              }"
              :border="true"
              :show-clear-button="true"
              :value="selectedItemGroup"
              @change="(group: string) => emitEvent('setItemGroup', group)"
            />
          </div>

          <div
            v-if="!items.length"
            class="flex min-h-0 flex-1 flex-col items-center justify-center gap-1 px-4 text-center"
          >
            <p class="text-lg font-medium text-ink-gray-7">
              {{ t`No items found` }}
            </p>
            <p class="text-sm text-ink-gray-5">
              {{ t`Try another item visibility or filter.` }}
            </p>
          </div>

          <ItemsTable
            v-else-if="tableView"
            :items="items"
            :item-qty-map="itemQuantityMap as ItemQtyMap"
            :item-visibility="itemVisibility"
            @add-item="(item) => emitEvent('addItem', item)"
          />

          <ItemsGrid
            v-else
            :items="items"
            @add-item="(item) => emitEvent('addItem', item)"
          />

          <div class="absolute bottom-4 left-4 flex gap-x-3 p-1">
            <POSQuickActions
              :sinv-doc="sinvDoc"
              :loyalty-points="loyaltyPoints"
              :loyalty-program="loyaltyProgram"
              :applied-coupons-count="appliedCouponsCount"
              @toggle-view="emitEvent('toggleView')"
              @emit-route-to-sinv-list="emitEvent('routeToSinvList')"
              @toggle-modal="
                (modalName, value) => emitEvent('toggleModal', modalName, value)
              "
            />
          </div>
        </div>
      </div>

      <div class="col-span-1 min-h-[40rem] xl:col-span-7 xl:min-h-0">
        <div class="flex h-full min-h-0 flex-col gap-3">
          <div
            class="p-4 bg-surface-base border rounded-4 min-h-0 flex-1 flex flex-col border-outline-gray-1"
          >
            <!-- Customer Search -->
            <div class="flex-none">
              <MultiLabelLink
                v-if="sinvDoc?.fieldMap"
                class="w-full"
                secondary-link="phone"
                :border="true"
                :value="sinvDoc?.party"
                :df="sinvDoc?.fieldMap.party"
                :show-clear-button="true"
                @change="(value: string) => $emit('setCustomer', value)"
              />
            </div>

            <SelectedItemTable
              :expanded-batch-id="expandedBatchId"
              @set-expanded-batch-id="
                (rowName) => $emit('setExpandedBatchId', rowName)
              "
              @apply-pricing-rule="emitEvent('applyPricingRule')"
              @selected-row="(row) => $emit('selectedRow', row)"
            />
          </div>

          <div
            class="p-3 bg-surface-base border rounded-4 border-outline-gray-1"
          >
            <div class="w-full grid grid-cols-2 gap-y-2 gap-x-3">
              <div class="flex flex-col justify-end">
                <div class="grid grid-cols-2 gap-2">
                  <FloatingLabelFloatInput
                    :df="{
                      label: t`Total Quantity`,
                      fieldtype: 'Float',
                      fieldname: 'totalQuantity',
                      minvalue: 0,
                      maxvalue: 1000,
                    }"
                    size="large"
                    :value="totalQuantity"
                    :read-only="true"
                    :text-right="true"
                  />

                  <FloatingLabelCurrencyInput
                    :df="{
                      label: t`Add'l Discounts`,
                      fieldtype: 'Currency',
                      fieldname: 'additionalDiscount',
                      minvalue: 0,
                    }"
                    size="large"
                    :value="additionalDiscounts"
                    :read-only="true"
                    :text-right="true"
                    @change="(amount: Money) => (additionalDiscounts = amount)"
                  />
                </div>

                <div class="mt-4 grid grid-cols-2 gap-2">
                  <FloatingLabelCurrencyInput
                    :df="{
                      label: t`Item Discounts`,
                      fieldtype: 'Currency',
                      fieldname: 'itemDiscounts',
                    }"
                    size="large"
                    :value="itemDiscounts"
                    :read-only="true"
                    :text-right="true"
                  />

                  <FloatingLabelCurrencyInput
                    v-if="sinvDoc?.fieldMap"
                    :df="sinvDoc?.fieldMap.grandTotal"
                    size="large"
                    :value="sinvDoc?.grandTotal"
                    :read-only="true"
                    :text-right="true"
                  />
                </div>
              </div>
              <div class="w-full">
                <div class="grid w-full min-w-0 grid-cols-2 gap-2">
                  <Button
                    size="lg"
                    variant="solid"
                    theme="gray"
                    class="w-full min-w-0"
                    :class="customButtonClass(saveButtonColour)"
                    :style="customButtonStyle(saveButtonColour)"
                    @click="$emit('saveInvoiceAction')"
                  >
                    <span>{{ t`Save` }}</span>
                  </Button>
                  <Button
                    size="lg"
                    variant="solid"
                    theme="gray"
                    class="w-full min-w-0"
                    :class="customButtonClass(cancelButtonColour)"
                    :style="customButtonStyle(cancelButtonColour)"
                    @click="() => $emit('clearValues')"
                  >
                    <span>{{ t`Cancel` }}</span>
                  </Button>
                </div>
                <div
                  class="grid w-full min-w-0 grid-cols-2 gap-2"
                  :class="`${isReturnInvoiceEnabledReturn ? 'mt-2' : 'mt-4'}`"
                >
                  <Button
                    size="lg"
                    variant="solid"
                    theme="gray"
                    class="w-full min-w-0"
                    :class="customButtonClass(heldButtonColour)"
                    :style="customButtonStyle(heldButtonColour)"
                    @click="emitEvent('toggleModal', 'SavedInvoice', true)"
                  >
                    <span>{{ t`held` }}</span>
                  </Button>

                  <Button
                    v-if="isReturnInvoiceEnabledReturn"
                    size="lg"
                    variant="solid"
                    theme="gray"
                    class="w-full min-w-0"
                    :class="customButtonClass(returnButtonColour)"
                    :style="customButtonStyle(returnButtonColour)"
                    @click="emitEvent('toggleModal', 'ReturnSalesInvoice', true)"
                  >
                    <span>{{ t`Return` }}</span>
                  </Button>
                  <Button
                    v-else
                    size="lg"
                    variant="solid"
                    theme="gray"
                    class="w-full min-w-0"
                    :class="customButtonClass(payButtonColour)"
                    :style="customButtonStyle(payButtonColour)"
                    @click="emitEvent('handlePaymentAction')"
                  >
                    <span>{{ t`Pay` }}</span>
                  </Button>
                </div>
                <Button
                  v-if="isReturnInvoiceEnabledReturn"
                  size="lg"
                  variant="solid"
                  theme="gray"
                  class="w-full mt-2"
                  :class="customButtonClass(payButtonColour)"
                  :style="customButtonStyle(payButtonColour)"
                  @click="emitEvent('handlePaymentAction')"
                >
                  <span>{{ t`Pay` }}</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Money } from 'pesa';
import { fyo } from 'src/initFyo';
import { getItem } from 'src/utils/pos';
import AlertModal from './AlertModal.vue';
import PaymentModal from './PaymentModal.vue';
import { Button } from 'frappe-ui';
import { getButtonTextColor } from 'src/utils/button';
import { defineComponent, PropType } from 'vue';
import PriceListModal from './PriceListModal.vue';
import ItemEnquiryModal from './ItemEnquiryModal.vue';
import { Item } from 'models/baseModels/Item/Item';
import CouponCodeModal from './CouponCodeModal.vue';
import POSQuickActions from './POSQuickActions.vue';
import { PosEmits } from 'src/components/POS/types';
import Link from 'src/components/Controls/Link.vue';
import SavedInvoiceModal from './SavedInvoiceModal.vue';
import OpenPOSShiftModal from './OpenPOSShiftModal.vue';
import ClosePOSShiftModal from './ClosePOSShiftModal.vue';
import LoyaltyProgramModal from './LoyaltyProgramModal.vue';
import { POSItem, ItemQtyMap } from 'src/components/POS/types';
import ItemsGrid from 'src/components/POS/ItemsGrid.vue';
import ItemsTable from 'src/components/POS/Classic/ItemsTable.vue';
import ReturnSalesInvoiceModal from './ReturnSalesInvoiceModal.vue';
import { POSProfile } from 'models/baseModels/POSProfile/PosProfile';
import MultiLabelLink from 'src/components/Controls/MultiLabelLink.vue';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import SelectedItemTable from 'src/components/POS/Classic/SelectedItemTable.vue';
import FloatingLabelFloatInput from 'src/components/POS/FloatingLabelFloatInput.vue';
import FloatingLabelCurrencyInput from 'src/components/POS/FloatingLabelCurrencyInput.vue';
import { AppliedCouponCodes } from 'models/baseModels/AppliedCouponCodes/AppliedCouponCodes';
import BatchSelectionModal from 'src/pages/POS/BatchSelectionModal.vue';

export default defineComponent({
  name: 'ClassicPOS',
  components: {
    Link,
    Button,
    ItemsGrid,
    AlertModal,
    ItemsTable,
    PaymentModal,
    MultiLabelLink,
    PriceListModal,
    ItemEnquiryModal,
    CouponCodeModal,
    POSQuickActions,
    OpenPOSShiftModal,
    SelectedItemTable,
    SavedInvoiceModal,
    ClosePOSShiftModal,
    LoyaltyProgramModal,
    FloatingLabelFloatInput,
    ReturnSalesInvoiceModal,
    FloatingLabelCurrencyInput,
    BatchSelectionModal,
  },
  props: {
    paidAmount: Money,
    tableView: Boolean,
    itemDiscounts: Money,
    openAlertModal: Boolean,
    isPosShiftOpen: Boolean,
    disablePayButton: Boolean,
    openPaymentModal: Boolean,
    openPriceListModal: Boolean,
    openItemEnquiryModal: Boolean,
    openCouponCodeModal: Boolean,
    openShiftCloseModal: Boolean,
    openSavedInvoiceModal: Boolean,
    openLoyaltyProgramModal: Boolean,
    openAppliedCouponsModal: Boolean,
    openReturnSalesInvoiceModal: Boolean,
    openBatchSelectionModal: Boolean,
    totalQuantity: {
      type: Number,
      default: 0,
    },
    loyaltyPoints: {
      type: Number,
      default: 0,
    },
    itemSearchTerm: {
      type: String,
      default: '',
    },
    selectedItemGroup: {
      type: String,
      default: '',
    },
    loyaltyProgram: {
      type: String,
      default: '',
    },
    appliedCouponsCount: {
      type: Number,
      default: 0,
    },
    sinvDoc: {
      type: Object as PropType<SalesInvoice | undefined>,
      default: undefined,
    },
    itemQuantityMap: {
      type: Object as PropType<ItemQtyMap>,
      default: () => ({}),
    },
    coupons: {
      type: Object as PropType<AppliedCouponCodes>,
      default: () => ({}),
    },
    items: {
      type: Array as PropType<POSItem[]>,
      default: () => [],
    },
    searchItems: {
      type: Array as PropType<POSItem[]>,
      default: () => [],
    },
    itemVisibility: {
      type: String,
      default: 'Inventory Items',
    },
    profile: {
      type: Object as PropType<POSProfile>,
      required: false,
      default: null,
    },
    batchAddedItems: {
      type: Array as () => string[],
      default: () => [],
    },
    selectedItemForBatch: {
      type: String,
      default: '',
    },
    expandedBatchId: {
      type: String as PropType<string | null | undefined>,
      default: undefined,
    },
  },
  emits: [
    'setExpandedBatchId',
    'addItem',
    'toggleView',
    'toggleModal',
    'setCustomer',
    'clearValues',
    'setItemGroup',
    'setPaidAmount',
    'setCouponsCount',
    'routeToSinvList',
    'handleItemSearch',
    'setPaymentMethod',
    'setTransferRefNo',
    'setLoyaltyPoints',
    'applyPricingRule',
    'saveInvoiceAction',
    'createTransaction',
    'setTransferAmount',
    'selectedInvoiceName',
    'selectedReturnInvoice',
    'setTransferClearanceDate',
    'saveAndContinue',
    'handlePaymentAction',
    'selectedRow',
    'batchSelected',
  ],
  data() {
    return {
      itemGroupFilter: '',
      additionalDiscounts: fyo.pesa(0),
    };
  },
  computed: {
    isReturnInvoiceEnabledReturn: () =>
      fyo.singles.AccountingSettings?.enableInvoiceReturns ?? undefined,
    isShiftOpenModalOpen: {
      get(): boolean {
        return !this.isPosShiftOpen;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'ShiftOpen');
        }
      },
    },
    isShiftCloseModalOpen: {
      get(): boolean {
        return this.openShiftCloseModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'ShiftClose', false);
        }
      },
    },
    isLoyaltyProgramModalOpen: {
      get(): boolean {
        return this.openLoyaltyProgramModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'LoyaltyProgram', false);
        }
      },
    },
    isBatchSelectionModalOpen: {
      get(): boolean {
        return this.openBatchSelectionModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'BatchSelection', false);
        }
      },
    },
    isSavedInvoiceModalOpen: {
      get(): boolean {
        return this.openSavedInvoiceModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'SavedInvoice', false);
        }
      },
    },
    isCouponCodeModalOpen: {
      get(): boolean {
        return this.openCouponCodeModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'CouponCode', false);
        }
      },
    },
    isPriceListModalOpen: {
      get(): boolean {
        return this.openPriceListModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'PriceList', false);
        }
      },
    },
    isItemEnquiryModalOpen: {
      get(): boolean {
        return this.openItemEnquiryModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'ItemEnquiry', false);
        }
      },
    },
    isPaymentModalOpen: {
      get(): boolean {
        return this.openPaymentModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'Payment', false);
        }
      },
    },
    isReturnSalesInvoiceModalOpen: {
      get(): boolean {
        return this.openReturnSalesInvoiceModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'ReturnSalesInvoice', false);
        }
      },
    },
    isAlertModalOpen: {
      get(): boolean {
        return this.openAlertModal;
      },
      set(value: boolean) {
        if (!value) {
          this.emitEvent('toggleModal', 'Alert', false);
        }
      },
    },
    saveButtonColour(): string | undefined {
      return resolveColour(
        this.profile?.saveButtonColour,
        fyo.singles.Defaults?.saveButtonColour
      );
    },
    cancelButtonColour(): string | undefined {
      return resolveColour(
        this.profile?.cancelButtonColour,
        fyo.singles.Defaults?.cancelButtonColour
      );
    },
    heldButtonColour(): string | undefined {
      return resolveColour(
        this.profile?.heldButtonColour,
        fyo.singles.Defaults?.heldButtonColour
      );
    },
    returnButtonColour(): string | undefined {
      return resolveColour(
        this.profile?.returnButtonColour,
        fyo.singles.Defaults?.returnButtonColour
      );
    },
    payButtonColour(): string | undefined {
      return resolveColour(
        this.profile?.payButtonColour,
        fyo.singles.Defaults?.payButtonColour
      );
    },
  },
  methods: {
    emitEvent(
      eventName: PosEmits,
      ...args: (string | boolean | Item | POSItem | number | Money)[]
    ) {
      this.$emit(eventName, ...args);
    },
    // POS profiles (and the Defaults single) can override the colour of the
    // action buttons. The colour drives two CSS variables consumed by the
    // scoped `.pos-custom-button` rules below, which also derive the hover and
    // active shades; `getButtonTextColor` picks a readable foreground.
    customButtonClass(colour?: string): string | undefined {
      return isCustomColour(colour) ? 'pos-custom-button' : undefined;
    },
    customButtonStyle(colour?: string): Record<string, string> | undefined {
      if (!isCustomColour(colour)) {
        return undefined;
      }

      return {
        '--pos-button-background': colour,
        '--pos-button-foreground': getButtonTextColor(colour),
      };
    },
    getItem,
  },
});

function resolveColour(...values: unknown[]): string | undefined {
  for (const value of values) {
    if (typeof value === 'string' && value) {
      return value;
    }
  }

  return undefined;
}

function isCustomColour(colour?: string): colour is string {
  return /^#[0-9a-f]{6}$/i.test(colour ?? '');
}
</script>

<style scoped>
.pos-custom-button:not(:disabled) {
  background-color: var(--pos-button-background);
  color: var(--pos-button-foreground);
}

.pos-custom-button:not(:disabled):hover {
  background-color: color-mix(in srgb, var(--pos-button-background), black 8%);
}

.pos-custom-button:not(:disabled):active {
  background-color: color-mix(in srgb, var(--pos-button-background), black 14%);
}
</style>
