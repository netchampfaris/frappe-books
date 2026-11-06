<template>
  <Dialog v-model:open="isOpen" :title="t`Alert`" size="md" :actions="actions">
    <p class="text-p-base text-ink-gray-7">
      {{ t`Clicking continue will remove all the selected items.` }}
    </p>
  </Dialog>
</template>

<script lang="ts">
import { Dialog, type DialogAction } from 'frappe-ui';
import { defineComponent } from 'vue';
import { routeTo } from 'src/utils/ui';

export default defineComponent({
  name: 'AlertModal',
  components: {
    Dialog,
  },
  props: {
    open: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:open', 'saveAndContinue'],
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
          label: this.t`Continue`,
          variant: 'subtle',
          theme: 'red',
          onClick: async () => {
            await routeTo('/list/SalesInvoice');
            this.closeModal();
          },
        },
        {
          label: this.t`Save and Continue`,
          variant: 'solid',
          theme: 'gray',
          onClick: () => this.$emit('saveAndContinue'),
        },
      ];
    },
  },
  methods: {
    closeModal() {
      this.$emit('update:open', false);
    },
  },
});
</script>
