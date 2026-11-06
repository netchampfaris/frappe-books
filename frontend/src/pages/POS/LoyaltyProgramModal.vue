<template>
  <Dialog
    v-model:open="isOpen"
    :title="t`Redeem Loyalty Points`"
    size="sm"
    :actions="actions"
  >
    <div class="flex items-center justify-end gap-2">
      <span class="lucide-coins size-5 text-ink-amber-5" aria-hidden="true" />

      <p class="text-ink-gray-8">
        {{ loyaltyPoints }} - ({{ loyaltyProgram }})
      </p>
    </div>

    <Int
      v-if="sinvDoc.fieldMap"
      class="mt-6 flex-shrink-0"
      :show-label="true"
      :border="true"
      :focus-input="true"
      :value="pendingLoyaltyPoints"
      :df="sinvDoc.fieldMap.loyaltyPoints"
      @keydown.enter="saveLoyaltyPoints"
      @change="setPendingLoyaltyPoints"
    />
  </Dialog>
</template>

<script lang="ts">
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import { defineComponent, inject } from 'vue';
import { t } from 'fyo';
import { Dialog, type DialogAction } from 'frappe-ui';
import { showToast } from 'src/utils/interactive';
import { ModelNameEnum } from 'models/types';
import Int from 'src/components/Controls/Int.vue';

export default defineComponent({
  name: 'LoyaltyProgramModal',
  components: {
    Dialog,
    Int,
  },
  props: {
    open: {
      type: Boolean,
      default: false,
    },
    loyaltyPoints: {
      type: Number,
      default: 0,
    },

    loyaltyProgram: {
      type: String,
      default: '',
    },
  },
  emits: ['setLoyaltyPoints', 'update:open'],
  setup() {
    return {
      sinvDoc: inject('sinvDoc') as SalesInvoice,
    };
  },
  data() {
    return {
      validationError: false,
      initialLoyaltyPoints: 0,
      pendingLoyaltyPoints: 0,
    };
  },
  computed: {
    isOpen: {
      get(): boolean {
        return this.open;
      },
      set(value: boolean) {
        if (!value) {
          this.cancelLoyaltyProgram();
        }
      },
    },
    actions(): DialogAction[] {
      return [
        {
          label: t`Cancel`,
          variant: 'subtle',
          theme: 'gray',
          onClick: () => this.cancelLoyaltyProgram(),
        },
        {
          label: t`Save`,
          variant: 'solid',
          theme: 'gray',
          onClick: () => this.saveLoyaltyPoints(),
        },
      ];
    },
  },
  watch: {
    open(value: boolean) {
      if (!value) {
        return;
      }

      this.initialLoyaltyPoints = this.sinvDoc.loyaltyPoints ?? 0;
      this.pendingLoyaltyPoints = this.initialLoyaltyPoints;
      this.validationError = false;
    },
  },
  methods: {
    setPendingLoyaltyPoints(value: number) {
      this.pendingLoyaltyPoints = value;
      this.validationError = false;
    },
    cancelLoyaltyProgram() {
      this.sinvDoc.loyaltyPoints = this.initialLoyaltyPoints;
      this.$emit('setLoyaltyPoints', this.initialLoyaltyPoints);
      this.$emit('update:open', false);
    },
    async applyLoyaltyPoints(newValue: number): Promise<boolean> {
      try {
        const partyData = await this.fyo.db.get(
          ModelNameEnum.Party,
          this.sinvDoc.party as string
        );

        if (!partyData.loyaltyProgram) {
          throw new Error(t`Customer is not enrolled in a loyalty program`);
        }

        const loyaltyProgramDoc = await this.fyo.db.getAll(
          ModelNameEnum.LoyaltyProgram,
          {
            fields: ['conversionFactor', 'toDate'],
            filters: { name: partyData.loyaltyProgram as string },
          }
        );

        const toDate = loyaltyProgramDoc[0]?.toDate as Date;
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (toDate && new Date(toDate).getTime() < today.getTime()) {
          throw new Error(t`Loyalty program has expired and cannot be applied`);
        }

        if (this.loyaltyPoints < newValue) {
          throw new Error(
            `${this.sinvDoc.party as string} only has ${this.loyaltyPoints} points`
          );
        }

        const loyaltyPoint =
          newValue * ((loyaltyProgramDoc[0]?.conversionFactor as number) || 0);

        if (this.sinvDoc.baseGrandTotal?.lt(loyaltyPoint)) {
          throw new Error(t`no need ${newValue} points to purchase this item`);
        }

        if (newValue < 0) {
          throw new Error(t`Points must be greater than 0`);
        }

        this.sinvDoc.loyaltyPoints = newValue;
        this.$emit('setLoyaltyPoints', newValue);

        this.validationError = false;
        return true;
      } catch (error) {
        this.validationError = true;

        showToast({
          type: 'error',
          message: t`${error as string}`,
        });

        return false;
      }
    },
    async saveLoyaltyPoints() {
      const applied = await this.applyLoyaltyPoints(this.pendingLoyaltyPoints);

      if (applied) {
        this.$emit('update:open', false);
      }
    },
  },
});
</script>
