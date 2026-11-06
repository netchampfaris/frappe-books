<template>
  <FrappeIcon
    v-if="phosphorIcon"
    :name="phosphorIcon"
    :size="size"
    :weight="weight"
    class="shrink-0"
    :class="colorClass"
  />
  <!--
    Fallback: a friendly name that is not in navIcons (say, one added to
    sidebarConfig.ts later) still renders its Lucide glyph via Books' own
    Icon component instead of rendering nothing.
  -->
  <BooksIcon v-else :name="name" :size="size" :active="active" />
</template>

<script lang="ts">
import { Icon as FrappeIcon } from 'frappe-ui';
import {
  PhCertificate,
  PhChartLine,
  PhCommand,
  PhDatabase,
  PhFlag,
  PhMagnifyingGlass,
  PhPackage,
  PhQuestion,
  PhReceipt,
  PhRocketLaunch,
  PhShoppingCart,
  PhSlidersHorizontal,
  PhSquaresFour,
  PhStack,
  PhStorefront,
} from '@phosphor-icons/vue';
import { Component, defineComponent, PropType } from 'vue';
import BooksIcon from './Icon.vue';

/**
 * The sidebar has its own icon set: Phosphor duotone reads better than a
 * single-weight line icon at nav size, and the active section can switch to
 * the filled weight. It stays scoped to the sidebar because frappe-ui's own
 * chrome (dialog close, dropdown carets) renders Lucide, so utility icons
 * everywhere else keep using Icon.vue and stay consistent with it.
 */
const navIcons: Record<string, Component> = {
  'search': PhMagnifyingGlass,
  'dashboard': PhSquaresFour,
  'sales': PhReceipt,
  'purchase': PhShoppingCart,
  'common-entries': PhStack,
  'reports': PhChartLine,
  'inventory': PhPackage,
  'pos': PhStorefront,
  'gst': PhCertificate,
  'settings': PhSlidersHorizontal,
  'general': PhRocketLaunch,
  'help-circle': PhQuestion,
  'command': PhCommand,
  'database': PhDatabase,
  'flag': PhFlag,
};

export default defineComponent({
  name: 'NavIcon',
  components: { BooksIcon, FrappeIcon },
  props: {
    name: { type: String, required: true },
    active: { type: Boolean, default: false },
    size: {
      type: [String, Number] as PropType<string | number>,
      default: 18,
    },
  },
  computed: {
    phosphorIcon(): Component | undefined {
      return navIcons[this.name];
    },
    weight(): string {
      return this.active ? 'fill' : 'duotone';
    },
    colorClass(): string {
      return this.active ? 'text-ink-gray-8' : 'text-ink-gray-6';
    },
  },
});
</script>
