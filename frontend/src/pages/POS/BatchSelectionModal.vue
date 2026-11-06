<template>
  <Dialog
    v-model:open="isOpen"
    :title="t`Select the Batch`"
    size="sm"
    :actions="actions"
  >
    <Link
      :df="{
        fieldname: 'batch',
        fieldtype: 'Link',
        target: 'Batch',
        label: t`Batch`,
        required: true,
        getOptions: getBatchOptions,
        filters: { item: itemCode },
      }"
      :value="selectedBatch"
      :border="true"
      :show-label="true"
      @change="(value: string) => (selectedBatch = value)"
    />
  </Dialog>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { t } from 'fyo';
import { showToast } from 'src/utils/interactive';
import { Dialog, type DialogAction } from 'frappe-ui';
import Link from 'src/components/Controls/Link.vue';
import { ModelNameEnum } from 'models/types';
import { fyo } from 'src/initFyo';

export default defineComponent({
  name: 'BatchSelectionModal',
  components: {
    Dialog,
    Link,
  },
  props: {
    open: {
      type: Boolean,
      default: false,
    },
    itemCode: {
      type: String,
      required: true,
    },
  },
  emits: ['update:open', 'batchSelected'],
  data() {
    return {
      selectedBatch: '' as string,
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
          label: t`Cancel`,
          variant: 'subtle',
          theme: 'gray',
          onClick: () => this.closeModal(),
        },
        {
          label: t`Select`,
          variant: 'solid',
          theme: 'gray',
          disabled: !this.selectedBatch,
          onClick: () => this.submitSelection(),
        },
      ];
    },
  },
  methods: {
    async getBatchOptions() {
      if (!this.itemCode) {
        return [];
      }

      try {
        const batches = (await fyo.db.getAll(ModelNameEnum.Batch, {
          filters: { item: this.itemCode },
          fields: ['name'],
        })) as { name: string; itemCode: string }[];

        return batches.map((b) => ({ label: b.name, value: b.name }));
      } catch (error) {
        showToast({ type: 'error', message: t`Failed to load batches` });
        return [];
      }
    },
    submitSelection() {
      this.$emit('batchSelected', this.selectedBatch);
      this.$emit('update:open', false);
      this.selectedBatch = '';
    },
    closeModal() {
      this.$emit('update:open', false);
      this.selectedBatch = '';
    },
  },
});
</script>
