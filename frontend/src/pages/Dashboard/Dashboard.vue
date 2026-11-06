<template>
  <div class="h-screen" style="width: var(--w-desk)">
    <PageHeader :title="t`Dashboard`">
      <PeriodSelector
        v-model="period"
        :options="['This Year', 'This Quarter', 'This Month', 'YTD']"
      />
    </PageHeader>

    <div
      class="no-scrollbar overflow-auto bg-surface-base"
      style="height: calc(100vh - var(--h-row-largest) - 1px)"
    >
      <div class="min-w-0">
        <Cashflow class="p-4" :common-period="period" />
        <FrappeDivider />
        <div class="grid grid-cols-1 md:grid-cols-2">
          <UnpaidInvoices
            :schema-name="'SalesInvoice'"
            :common-period="period"
            class="min-w-0 border-e border-outline-gray-1"
          />
          <UnpaidInvoices
            :schema-name="'PurchaseInvoice'"
            :common-period="period"
          />
        </div>
        <FrappeDivider />
        <div class="grid grid-cols-1 xl:grid-cols-2">
          <ProfitAndLoss
            class="min-w-0 w-full p-4 border-e border-outline-gray-1"
            :common-period="period"
          />
          <Expenses
            class="min-w-0 w-full p-4"
            :common-period="period"
          />
        </div>
        <FrappeDivider />
      </div>
    </div>
  </div>
</template>

<script>
import { Divider as FrappeDivider } from 'frappe-ui';
import PageHeader from 'src/components/PageHeader.vue';
import UnpaidInvoices from './UnpaidInvoices.vue';
import Cashflow from './Cashflow.vue';
import Expenses from './Expenses.vue';
import PeriodSelector from './PeriodSelector.vue';
import ProfitAndLoss from './ProfitAndLoss.vue';
import { docsPathRef } from 'src/utils/refs';

export default {
  name: 'Dashboard',
  components: {
    FrappeDivider,
    PageHeader,
    Cashflow,
    ProfitAndLoss,
    Expenses,
    PeriodSelector,
    UnpaidInvoices,
  },
  data() {
    return { period: 'This Year' };
  },
  activated() {
    docsPathRef.value = 'books/dashboard';
  },
  deactivated() {
    docsPathRef.value = '';
  },
};
</script>
