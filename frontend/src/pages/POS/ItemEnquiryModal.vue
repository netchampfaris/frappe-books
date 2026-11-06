<template>
  <Dialog
    v-model:open="isOpen"
    :title="t`Item Enquiry`"
    size="sm"
    :actions="actions"
  >
    <div class="flex flex-col gap-5">
      <Link
        :df="{
          fieldname: 'item',
          fieldtype: 'Link',
          target: 'Item',
          label: t`Item`,
          required: true,
        }"
        :value="ItemEnquiry.item"
        :border="true"
        :show-label="true"
        @change="(value: string) => (ItemEnquiry.item = value)"
      />

      <Text
        :df="{
          fieldname: 'description',
          fieldtype: 'Text',
          label: t`Description`,
        }"
        :value="ItemEnquiry.description"
        :border="true"
        :show-label="true"
        @change="(value: string) => (ItemEnquiry.description = value)"
      />

      <Link
        :df="{
          fieldname: 'customer',
          fieldtype: 'Link',
          target: 'Party',
          label: t`Customer`,
        }"
        :value="ItemEnquiry.customer"
        :border="true"
        :show-label="true"
        @change="
          (value: string) => {
            ItemEnquiry.customer = value;
            updateCustomerContact(value);
          }
        "
      />

      <Data
        :df="{
          fieldname: 'contact',
          fieldtype: 'Data',
          label: t`Contact`,
        }"
        :value="ItemEnquiry.contact"
        :border="true"
        :show-label="true"
        @change="(value: string) => (ItemEnquiry.contact = value)"
      />

      <Link
        :df="{
          fieldname: 'similarProduct',
          fieldtype: 'Link',
          target: 'Item',
          label: t`Similar Product`,
        }"
        :value="ItemEnquiry.similarProduct"
        :border="true"
        :show-label="true"
        @change="(value: string) => (ItemEnquiry.similarProduct = value)"
      />
    </div>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { t } from 'fyo';
import { showToast } from 'src/utils/interactive';
import { Dialog, type DialogAction } from 'frappe-ui';
import Link from 'src/components/Controls/Link.vue';
import Text from 'src/components/Controls/Text.vue';
import Data from 'src/components/Controls/Data.vue';
import { ItemEnquiry } from 'models/baseModels/ItemEnquiry/ItemEnquiry';
import { ModelNameEnum } from 'models/types';
import { DocValueMap } from 'fyo/core/types';

export default defineComponent({
  name: 'ItemEnquiryModal',
  components: {
    Dialog,
    Link,
    Text,
    Data,
  },
  props: {
    open: { type: Boolean, default: false },
    customer: { type: String, default: '' },
  },
  emits: ['update:open'],
  data() {
    return {
      ItemEnquiry: {} as ItemEnquiry,
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
          label: t`Submit`,
          variant: 'solid',
          theme: 'gray',
          onClick: () => this.submitForm(),
        },
      ];
    },
  },
  watch: {
    open: {
      async handler(isOpen: boolean) {
        if (!isOpen) {
          return;
        }

        this.clearValues();
        if (!this.customer) {
          return;
        }

        this.ItemEnquiry.customer = this.customer;
        await this.updateCustomerContact(this.customer);
      },
    },
  },
  methods: {
    async updateCustomerContact(customer: string) {
      this.ItemEnquiry.contact =
        ((await this.fyo.getValue('Party', customer, 'phone')) as string) || '';
    },

    async submitForm() {
      try {
        const itemEnquiryDoc = this.fyo.doc.getNewDoc(
          ModelNameEnum.ItemEnquiry,
          this.ItemEnquiry as DocValueMap
        );
        await itemEnquiryDoc.sync();
        showToast({
          type: 'success',
          message: t`Item enquiry submitted`,
        });
        this.clearValues();
        this.$emit('update:open', false);
      } catch (error) {
        showToast({
          type: 'error',
          message: t`${error as string}`,
        });
      }
    },
    clearValues() {
      this.ItemEnquiry = {} as ItemEnquiry;
    },
    closeModal() {
      this.clearValues();
      this.$emit('update:open', false);
    },
  },
});
</script>
