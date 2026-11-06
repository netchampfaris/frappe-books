<template>
  <Dialog
    v-model:open="isOpen"
    :title="t`Open POS Shift`"
    size="2xl"
    :actions="actions"
  >
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="min-w-0">
        <h2 class="text-lg font-medium text-ink-gray-8">
          {{ t`Cash In Denominations` }}
        </h2>

        <Table
          v-if="isValuesSeeded"
          class="mt-4 text-base"
          :df="getField('openingCash')"
          :show-header="true"
          :border="true"
          :value="posShiftDoc?.openingCash"
          @row-change="handleChange"
        />
      </div>

      <div class="min-w-0">
        <h2 class="text-lg font-medium text-ink-gray-8">
          {{ t`Opening Amount` }}
        </h2>

        <Table
          v-if="isValuesSeeded"
          class="mt-4 text-base"
          :df="getField('openingAmounts')"
          :show-header="true"
          :border="true"
          :max-rows-before-overflow="4"
          :value="posShiftDoc?.openingAmounts"
          :read-only="false"
          :allow-add-remove-rows="false"
          @row-change="handleChange"
        />
      </div>
    </div>
  </Dialog>
</template>

<script lang="ts">
import Table from 'src/components/Controls/Table.vue';
import { AccountTypeEnum } from 'models/baseModels/Account/types';
import { ModelNameEnum } from 'models/types';
import { Money } from 'pesa';
import { POSOpeningShift } from 'models/inventory/Point of Sale/POSOpeningShift';
import { computed } from 'vue';
import { defineComponent } from 'vue';
import { Dialog, type DialogAction } from 'frappe-ui';
import { fyo } from 'src/initFyo';
import { showToast } from 'src/utils/interactive';
import { t } from 'fyo';
import { ValidationError } from 'fyo/utils/errors';
import { getPOSOpeningShiftDoc } from 'src/utils/pos';

export default defineComponent({
  name: 'OpenPOSShift',
  components: { Dialog, Table },
  provide() {
    return {
      doc: computed(() => this.posShiftDoc),
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
      posShiftDoc: undefined as POSOpeningShift | undefined,

      isValuesSeeded: false,
      isDismissed: false,
    };
  },
  computed: {
    isOpen: {
      get(): boolean {
        return this.open && !this.isDismissed && this.isValuesSeeded;
      },
      set(value: boolean) {
        if (!value) {
          this.handleDismiss();
        }
      },
    },
    actions(): DialogAction[] {
      return [
        {
          label: t`Back`,
          variant: 'subtle',
          theme: 'gray',
          onClick: () => this.handleDismiss(),
        },
        {
          label: t`Submit`,
          variant: 'solid',
          theme: 'gray',
          onClick: () => this.handleSubmit(),
        },
      ];
    },
    getDefaultCashDenominations() {
      return this.fyo.singles.Defaults?.posCashDenominations;
    },
    posCashAccount() {
      return fyo.singles.POSSettings?.cashAccount;
    },
    posOpeningCashAmount(): Money {
      return this.posShiftDoc?.openingCashAmount as Money;
    },
  },
  async mounted() {
    this.isValuesSeeded = false;
    this.posShiftDoc = await getPOSOpeningShiftDoc(fyo);

    await this.seedDefaults();
    this.isValuesSeeded = true;
  },
  activated() {
    this.isDismissed = false;
  },
  deactivated() {
    this.isDismissed = true;
  },
  methods: {
    handleDismiss() {
      this.isDismissed = true;
      this.$router.back();
    },
    async seedDefaultCashDenomiations() {
      if (!this.posShiftDoc) {
        return;
      }

      this.posShiftDoc.openingCash = [];
      const denominations = this.getDefaultCashDenominations;

      if (!denominations) {
        return;
      }

      for (const row of denominations) {
        await this.posShiftDoc.append('openingCash', {
          denomination: row.denomination,
          count: 0,
        });
      }
    },
    async seedPaymentMethods() {
      if (!this.posShiftDoc) {
        return;
      }

      this.posShiftDoc.openingAmounts = [];

      const paymentMethods = (
        (await this.fyo.db.getAll(ModelNameEnum.PaymentMethod, {
          fields: ['name'],
        })) as { name: string }[]
      ).map((doc) => ({ paymentMethod: doc.name, amount: fyo.pesa(0) }));

      await this.posShiftDoc.set('openingAmounts', paymentMethods);
    },
    async seedDefaults() {
      if (!!this.posShiftDoc?.isShiftOpen) {
        return;
      }

      await this.seedDefaultCashDenomiations();
      await this.seedPaymentMethods();
    },
    getField(fieldname: string) {
      return this.fyo.getField(ModelNameEnum.POSOpeningShift, fieldname);
    },
    setOpeningCashAmount() {
      if (!this.posShiftDoc?.openingAmounts) {
        return;
      }

      this.posShiftDoc.openingAmounts.map((row) => {
        if (row.paymentMethod === 'Cash') {
          row.amount = this.posShiftDoc?.openingCashAmount as Money;
        }
      });
    },
    handleChange() {
      this.setOpeningCashAmount();
    },
    async handleSubmit() {
      try {
        if (this.posShiftDoc?.openingCashAmount.isNegative()) {
          throw new ValidationError(
            t`Opening Cash Amount can not be negative.`
          );
        }

        await this.posShiftDoc?.setMultiple({
          isShiftOpen: true,
          openingDate: new Date(),
        });

        await this.posShiftDoc?.sync();
        await this.fyo.singles.POSSettings?.setAndSync('isShiftOpen', true);

        if (!this.posShiftDoc?.openingCashAmount.isZero()) {
          const jvDoc = fyo.doc.getNewDoc(ModelNameEnum.JournalEntry, {
            entryType: 'Journal Entry',
          });

          await jvDoc.append('accounts', {
            account: this.posCashAccount,
            debit: this.posShiftDoc?.openingCashAmount as Money,
            credit: this.fyo.pesa(0),
          });

          await jvDoc.append('accounts', {
            account: AccountTypeEnum.Cash,
            debit: this.fyo.pesa(0),
            credit: this.posShiftDoc?.openingCashAmount as Money,
          });

          await (await jvDoc.sync()).submit();
        }

        this.$emit('update:open', false);
      } catch (error) {
        showToast({
          type: 'error',
          message: t`${error as string}`,
          duration: 'short',
        });
        return;
      }
    },
  },
});
</script>
