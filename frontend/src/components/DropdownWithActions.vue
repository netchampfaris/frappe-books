<template>
  <Dropdown
    v-if="actions && actions.length"
    class="text-xs"
    :items="items"
    :doc="doc"
    :disabled="disabled"
    right
  >
    <template #default>
      <FrappeButton
        v-if="isIconOnly"
        :variant="variant"
        theme="gray"
        icon="lucide-ellipsis"
        :disabled="disabled"
        :tooltip="triggerLabel"
        :aria-label="triggerLabel"
      />
      <FrappeButton
        v-else
        :variant="variant"
        theme="gray"
        :disabled="disabled"
        :tooltip="triggerLabel"
      >
        <slot />
      </FrappeButton>
    </template>
  </Dropdown>
</template>

<script lang="ts">
import { Doc } from 'fyo/model/doc';
import { Action } from 'fyo/model/types';
import { Button as FrappeButton } from 'frappe-ui';
import { t } from 'fyo';
import Dropdown from 'src/components/Dropdown.vue';
import { DropdownItem } from 'src/utils/types';
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'DropdownWithActions',
  inheritAttrs: false,
  components: {
    Dropdown,
    FrappeButton,
  },
  inject: {
    injectedDoc: {
      from: 'doc',
      default: undefined,
    },
  },
  props: {
    actions: { type: Array as PropType<Action[]>, default: () => [] },
    type: { type: String, default: 'secondary' },
    icon: { type: Boolean, default: true },
    disabled: { type: Boolean, default: false },
  },
  computed: {
    /** Actions come from model code, which types a group as primary or not. */
    variant(): 'solid' | 'subtle' {
      return this.type === 'primary' ? 'solid' : 'subtle';
    },
    isIconOnly(): boolean {
      return this.icon && !this.$slots.default;
    },
    triggerLabel(): string {
      const title = this.$attrs.title;
      return typeof title === 'string' && title ? title : t`Actions`;
    },
    doc() {
      // @ts-ignore
      const doc = this.injectedDoc;
      if (doc instanceof Doc) {
        return doc;
      }

      return undefined;
    },
    items(): DropdownItem[] {
      return this.actions.map(({ label, group, theme, action }) => ({
        label,
        group,
        action,
        theme,
      }));
    },
  },
});
</script>
