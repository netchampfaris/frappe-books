<template>
  <Dialog
    v-model:open="isOpen"
    :title="t`Close POS Shift`"
    size="4xl"
    :actions="actions"
  >
    <h2 class="mb-2 text-lg font-medium text-ink-gray-8">
      {{ t`Closing Cash` }}
    </h2>
    <Table
      v-if="isValuesSeeded"
      class="text-base"
      :df="getField('closingCash')"
      :show-header="true"
      :border="true"
      :value="posClosingShiftDoc?.closingCash ?? []"
      :read-only="false"
      @row-change="updateClosingAmounts"
    />

    <h2 class="mt-6 mb-2 text-lg text-ink-gray-8 font-medium">
      {{ t`Closing Amounts` }}
    </h2>
    <Table
      v-if="isValuesSeeded"
      class="text-base"
      :df="getField('closingAmounts')"
      :show-header="true"
      :border="true"
      :value="posClosingShiftDoc?.closingAmounts"
      :read-only="false"
      :allow-add-remove-rows="false"
      @row-change="updateClosingAmounts"
    />
  </Dialog>
</template>

<script lang="ts">
import Table from 'src/components/Controls/Table.vue';
import { ModelNameEnum } from 'models/types';
import { Money } from 'pesa';
import { OpeningAmounts } from 'models/inventory/Point of Sale/OpeningAmounts';
import { POSOpeningShift } from 'models/inventory/Point of Sale/POSOpeningShift';
import { computed } from 'vue';
import { defineComponent } from 'vue';
import { Dialog, type DialogAction } from 'frappe-ui';
import { fyo } from 'src/initFyo';
import { showToast } from 'src/utils/interactive';
import { t } from 'fyo';
import {
  validateClosingAmounts,
  transferPOSCashAndWriteOff,
  getPOSOpeningShiftDoc,
} from 'src/utils/pos';
import { POSClosingShift } from 'models/inventory/Point of Sale/POSClosingShift';
import { ForbiddenError } from 'fyo/utils/errors';

export default defineComponent({
  name: 'ClosePOSShiftModal',
  components: { Dialog, Table },
  provide() {
    return {
      doc: computed(() => this.posClosingShiftDoc),
    };
  },
  props: {
    open: {
      default: false,
      type: Boolean,
    },
  },
  emits: ['update:open'],
  data() {
    return {
      isValuesSeeded: false,

      posOpeningShiftDoc: undefined as POSOpeningShift | undefined,
      posClosingShiftDoc: undefined as POSClosingShift | undefined,
      transactedAmount: {} as Record<string, Money> | undefined,
    };
  },
  computed: {
    isOpen: {
      get(): boolean {
        return this.open && this.isValuesSeeded;
      },
      set(value: boolean) {
        if (!value) {
          this.$emit('update:open', false);
        }
      },
    },
    actions(): DialogAction[] {
      return [
        {
          label: t`Cancel`,
          variant: 'subtle',
          theme: 'gray',
          onClick: () => this.$emit('update:open', false),
        },
        {
          label: t`Submit`,
          variant: 'solid',
          theme: 'gray',
          onClick: async () => {
            await this.handleSubmit();
          },
        },
      ];
    },
    isOnline() {
      return !!navigator.onLine;
    },
  },
  watch: {
    open: {
      async handler(value: boolean) {
        if (value) {
          await this.prepareShift();
        }
      },
    },
  },
  methods: {
    async prepareShift() {
      this.isValuesSeeded = false;
      this.posClosingShiftDoc = fyo.doc.getNewDoc(
        ModelNameEnum.POSClosingShift
      ) as POSClosingShift;
      await this.setTransactedAmount();
      await this.seedValues();
    },
    async setTransactedAmount() {
      this.posOpeningShiftDoc = await getPOSOpeningShiftDoc(fyo);

      const fromDate = this.posOpeningShiftDoc?.openingDate as Date;
      if (!fromDate) {
        return;
      }

      this.transactedAmount = await fyo.db.getPOSTransactedAmount(
        fromDate,
        new Date()
      );
    },
    async seedClosingCash() {
      if (!this.posClosingShiftDoc) {
        return;
      }

      this.posClosingShiftDoc.closingCash = [];

      for (const row of this.posOpeningShiftDoc?.openingCash ?? []) {
        await this.posClosingShiftDoc?.append('closingCash', {
          count: row.count,
          denomination: row.denomination as Money,
        });
      }
    },
    updateClosingAmounts() {
      if (!this.posClosingShiftDoc?.closingAmounts) {
        return;
      }

      this.posClosingShiftDoc.closingAmounts.forEach((row) => {
        if (row.paymentMethod === 'Cash') {
          row.closingAmount = this.posClosingShiftDoc
            ?.closingCashAmount as Money;
        }

        row.closingAmount ??= fyo.pesa(0);
        row.differenceAmount = row.closingAmount.sub(
          row.expectedAmount as Money
        );
      });
    },
    async seedClosingAmounts() {
      if (!this.posClosingShiftDoc || !this.posOpeningShiftDoc) {
        return;
      }

      this.posClosingShiftDoc.closingAmounts = [];

      const openingAmounts = this.posOpeningShiftDoc
        ?.openingAmounts as OpeningAmounts[];

      for (const row of openingAmounts) {
        if (!row.paymentMethod) {
          return;
        }

        let expectedAmount = row.amount ?? fyo.pesa(0);

        if (this.transactedAmount) {
          expectedAmount = expectedAmount.add(
            this.transactedAmount[row.paymentMethod] ?? fyo.pesa(0)
          );
        }

        await this.posClosingShiftDoc.append('closingAmounts', {
          paymentMethod: row.paymentMethod,
          openingAmount: row.amount,
          closingAmount: fyo.pesa(0),
          expectedAmount: expectedAmount,
          differenceAmount: fyo.pesa(0),
        });
      }
    },
    async seedValues() {
      this.isValuesSeeded = false;
      await this.seedClosingCash();
      await this.seedClosingAmounts();
      this.updateClosingAmounts();
      this.isValuesSeeded = true;
    },
    getField(fieldname: string) {
      return fyo.getField(ModelNameEnum.POSClosingShift, fieldname);
    },
    async handleSubmit() {
      try {
        if (!this.isOnline) {
          throw new ForbiddenError(
            t`Device is offline. Please connect to a network to continue.`
          );
        }

        validateClosingAmounts(this.posClosingShiftDoc as POSClosingShift);
        await this.posClosingShiftDoc?.set('closingDate', new Date());
        await this.posClosingShiftDoc?.set(
          'openingShift',
          this.posOpeningShiftDoc?.name
        );
        await this.posClosingShiftDoc?.sync();
        await transferPOSCashAndWriteOff(
          fyo,
          this.posClosingShiftDoc as POSClosingShift
        );

        await this.fyo.singles.POSSettings?.setAndSync('isShiftOpen', false);
        this.$emit('update:open', false);
      } catch (error) {
        return showToast({
          type: 'error',
          message: t`${error as string}`,
          duration: 'short',
        });
      }
    },
  },
});
</script>
