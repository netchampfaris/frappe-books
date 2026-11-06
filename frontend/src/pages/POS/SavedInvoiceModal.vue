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
        @keyup.enter="handleEnterKey"
      />

      <FrappeTabButtons
        :model-value="savedInvoiceList ? 'saved' : 'submitted'"
        :options="invoiceTabs"
        class="mt-2 w-full"
        fluid
        @update:model-value="showSavedInvoices($event === 'saved')"
      />

      <InvoiceSelectionTable
        v-model="selectedInvoiceName"
        :rows="filteredInvoices"
        :fields="tableFields"
        :ratios="ratio"
        :empty-text="t`No invoices found`"
      />
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
import {
  Dialog,
  TabButtons as FrappeTabButtons,
  TextInput as FrappeTextInput,
  type DialogAction,
} from 'frappe-ui';

export default defineComponent({
  name: 'SavedInvoiceModal',
  components: {
    Dialog,
    InvoiceSelectionTable,
    FrappeTextInput,
    FrappeTabButtons,
  },
  props: {
    open: Boolean,
  },
  emits: ['update:open', 'selectedInvoiceName'],
  data() {
    return {
      savedInvoiceList: true,
      savedInvoices: [] as SalesInvoice[],
      submittedInvoices: [] as SalesInvoice[],
      invoiceSearchTerm: '',
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
          label: this.t`Open Invoice`,
          variant: 'solid',
          theme: 'gray',
          disabled: !this.selectedInvoiceName,
          onClick: () => this.openSelectedInvoice(),
        },
      ];
    },
    ratio() {
      return [1, 1, 1, 0.8];
    },
    invoiceTabs() {
      return [
        { value: 'saved', label: this.t`Saved` },
        { value: 'submitted', label: this.t`Submitted` },
      ];
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
      const invoices = this.savedInvoiceList ? this.savedInvoices : this.submittedInvoices;
      return invoices.filter((invoice) =>
        (invoice.name as string).toLowerCase().includes(this.invoiceSearchTerm.toLowerCase()),
      );
    },
  },
  watch: {
    async open(newVal) {
      if (newVal) {
        this.selectedInvoiceName = '';
        await this.setSavedInvoices();
        await this.setSubmittedInvoices();
      }
    },
    invoiceSearchTerm() {
      this.selectedInvoiceName = '';
    },
  },
  async mounted() {
    await this.setSavedInvoices();
    await this.setSubmittedInvoices();
  },
  async activated() {
    await this.setSavedInvoices();
    await this.setSubmittedInvoices();
  },

  methods: {
    async setSavedInvoices() {
      this.savedInvoices = (await this.fyo.db.getAll(ModelNameEnum.SalesInvoice, {
        fields: [],
        filters: { isPOS: true, submitted: false },
      })) as SalesInvoice[];
    },
    async setSubmittedInvoices() {
      const invoices = (await this.fyo.db.getAll(ModelNameEnum.SalesInvoice, {
        fields: [],
        filters: { isPOS: true, submitted: true, returnAgainst: null },
      })) as SalesInvoice[];

      this.submittedInvoices = invoices.filter(
        (invoice) => !(invoice.outstandingAmount as Money).isZero(),
      );
    },
    closeModal() {
      this.selectedInvoiceName = '';
      this.$emit('update:open', false);
    },
    openSelectedInvoice() {
      const selectedInvoice = this.filteredInvoices.find(
        (invoice) => invoice.name === this.selectedInvoiceName,
      );
      if (!selectedInvoice) {
        return;
      }

      this.$emit('selectedInvoiceName', selectedInvoice);
      this.closeModal();
    },
    showSavedInvoices(saved: boolean) {
      this.savedInvoiceList = saved;
      this.selectedInvoiceName = '';
    },
    handleEnterKey() {
      if (this.filteredInvoices.length === 1) {
        this.selectedInvoiceName = String(this.filteredInvoices[0].name);
      }
    },
  },
});
</script>
