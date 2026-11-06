<template>
  <Dialog
    v-model:open="isOpen"
    :title="t`Apply Price List`"
    size="sm"
    :actions="actions"
  >
    <div class="flex items-end gap-2">
      <Link
        v-if="sinvDoc.fieldMap"
        class="min-w-0 flex-1"
        :border="true"
        :value="selectedPriceList"
        :focus-input="true"
        :df="sinvDoc.fieldMap.priceList"
        @change="(value) => (selectedPriceList = value ?? '')"
      />

      <Button
        icon="lucide-trash-2"
        theme="red"
        variant="ghost"
        :tooltip="t`Remove price list`"
        :aria-label="t`Remove price list`"
        @click="removePriceList"
      />
    </div>
  </Dialog>
</template>

<script lang="ts">
import { t } from 'fyo';
import { defineComponent, inject } from 'vue';
import { showToast } from 'src/utils/interactive';
import Link from 'src/components/Controls/Link.vue';
import { Button, Dialog, type DialogAction } from 'frappe-ui';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';

export default defineComponent({
  name: 'PriceListModal',
  components: {
    Link,
    Button,
    Dialog,
  },
  props: {
    open: Boolean,
  },
  emits: ['update:open'],
  setup() {
    return {
      sinvDoc: inject('sinvDoc') as SalesInvoice,
    };
  },
  data() {
    return {
      selectedPriceList: '',
    };
  },
  computed: {
    isOpen: {
      get(): boolean {
        return this.open;
      },
      set(value: boolean) {
        if (!value) {
          this.cancelPriceList();
        }
      },
    },
    actions(): DialogAction[] {
      return [
        {
          label: t`Cancel`,
          variant: 'subtle',
          theme: 'gray',
          onClick: () => this.cancelPriceList(),
        },
        {
          label: t`Save`,
          variant: 'solid',
          theme: 'gray',
          onClick: () => this.setPriceList(),
        },
      ];
    },
  },
  watch: {
    open(value: boolean) {
      if (value) {
        this.selectedPriceList = this.sinvDoc.priceList ?? '';
      }
    },
  },
  methods: {
    removePriceList() {
      this.selectedPriceList = '';
    },
    async setPriceList() {
      try {
        await this.sinvDoc.set('priceList', this.selectedPriceList);
        this.$emit('update:open', false);
      } catch (error) {
        showToast({
          type: 'error',
          message: t`${error as string}`,
        });
      }
    },
    cancelPriceList() {
      this.$emit('update:open', false);
    },
  },
});
</script>
