<template>
  <Dialog
    v-model:open="isOpen"
    :title="t`Invoices`"
    size="2xl"
    :actions="actions"
  >
    <div class="flex h-[calc(100vh-18rem)] max-h-[32rem] min-h-0 flex-col">
      <FrappeTextInput
        v-model="invoiceSearchTerm"
        type="text"
        :placeholder="t`Search by invoice name`"
        class="w-full"
        variant="outline"
        size="md"
        @keydown.enter="handleSearchEnter"
      />

      <Divider class="mt-2" />

      <InvoiceSelectionTable
        v-model="selectedInvoiceName"
        :rows="paginatedInvoices"
        :fields="tableFields"
        :ratios="ratio"
        :empty-text="t`No invoices found`"
      />

      <div v-if="filteredInvoices.length" class="mt-1 mb-1">
        <Paginator
          :item-count="filteredInvoices.length"
          :allowed-counts="[20, 40, -1]"
          @index-change="setPageIndices"
        />
      </div>
    </div>
  </Dialog>
</template>

<script lang="ts">
import InvoiceSelectionTable from 'src/components/POS/InvoiceSelectionTable.vue';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import { defineComponent } from 'vue';
import { ModelNameEnum } from 'models/types';
import { Field } from 'schemas/types';
import { Money } from 'pesa';
import Paginator from 'src/components/Paginator.vue';
import {
  Dialog,
  Divider,
  TextInput as FrappeTextInput,
  type DialogAction,
} from 'frappe-ui';

export default defineComponent({
  name: 'ReturnSalesInvoice',
  components: {
    Dialog,
    Divider,
    InvoiceSelectionTable,
    Paginator,
    FrappeTextInput,
  },
  props: {
    open: Boolean,
  },
  emits: ['update:open', 'selectedReturnInvoice'],
  data() {
    return {
      returnedInvoices: [] as SalesInvoice[],
      invoiceSearchTerm: '',
      pageStart: 0,
      pageEnd: 20,
      selectedInvoiceName: '',
    };
  },
  computed: {
    isOpen: {
      get(): boolean {
        return this.open;
      },
      set(value: boolean) {
        if (!value) {
          this.closeModal();
        }
      },
    },
    actions(): DialogAction[] {
      return [
        {
          label: this.t`Cancel`,
          variant: 'subtle',
          theme: 'gray',
          onClick: () => this.closeModal(),
        },
        {
          label: this.t`Create Return`,
          variant: 'solid',
          theme: 'gray',
          disabled: !this.selectedInvoiceName,
          onClick: () => this.returnSelectedInvoice(),
        },
      ];
    },
    ratio() {
      return [1, 1, 1, 0.8];
    },
    tableFields() {
      return [
        {
          fieldname: 'name',
          label: 'Name',
          fieldtype: 'Data',
          readOnly: true,
        },
        {
          fieldname: 'party',
          fieldtype: 'Data',
          label: 'Customer',
          placeholder: 'Customer',
          readOnly: true,
        },
        {
          fieldname: 'date',
          label: 'Date',
          fieldtype: 'Date',
          readOnly: true,
        },
        {
          fieldname: 'grandTotal',
          label: 'Grand Total',
          fieldtype: 'Currency',
          readOnly: true,
        },
      ] as Field[];
    },
    filteredInvoices() {
      return this.returnedInvoices.filter((invoice) =>
        (invoice.name as string)
          .toLowerCase()
          .includes(this.invoiceSearchTerm.toLowerCase())
      );
    },
    paginatedInvoices() {
      return this.filteredInvoices.slice(this.pageStart, this.pageEnd);
    },
  },
  watch: {
    async open(newVal) {
      if (newVal) {
        this.selectedInvoiceName = '';
        await this.setReturnedInvoices();
      }
    },
    invoiceSearchTerm() {
      this.pageStart = 0;
      this.pageEnd = this.pageEnd - this.pageStart || 20;
      this.selectedInvoiceName = '';
    },
  },
  async mounted() {
    await this.setReturnedInvoices();
  },
  async activated() {
    await this.setReturnedInvoices();
  },

  methods: {
    closeModal() {
      this.selectedInvoiceName = '';
      this.$emit('update:open', false);
    },
    returnSelectedInvoice() {
      if (!this.selectedInvoiceName) {
        return;
      }

      this.$emit('selectedReturnInvoice', this.selectedInvoiceName);
      this.closeModal();
    },
    handleSearchEnter() {
      if (this.filteredInvoices.length === 1) {
        this.selectedInvoiceName = String(this.filteredInvoices[0].name);
      }
    },
    setPageIndices({ start, end }: { start: number; end: number }) {
      this.pageStart = start;
      this.pageEnd = end;
      this.selectedInvoiceName = '';
    },
    async setReturnedInvoices() {
      const allInvoices = await this.fyo.db.getAll(ModelNameEnum.SalesInvoice, {
        fields: [],
        filters: {
          isPOS: true,
          submitted: true,
          cancelled: false,
        },
      });

      const returnedInvoiceNames = allInvoices
        .filter((inv) => {
          if (inv.isFullyReturned || inv.returnAgainst) {
            return false;
          }

          if (inv.isReturned && !inv.isFullyReturned) {
            return true;
          }

          if (!inv.isReturned && !inv.returnAgainst) {
            return true;
          }

          if (!inv.isReturned && !(inv.outstandingAmount as Money).isZero()) {
            return true;
          }

          return false;
        })
        .map((inv) => inv.name);
      this.returnedInvoices = allInvoices.filter((inv) =>
        returnedInvoiceNames.includes(inv.name)
      ) as SalesInvoice[];
    },
  },
});
</script>
