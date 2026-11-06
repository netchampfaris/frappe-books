<template>
  <FrappeTree :nodes="nodes" node-key="key">
    <template #item-label="{ node }">
      <span
        class="flex min-w-0 flex-1 flex-wrap items-center gap-2 text-sm text-ink-gray-6"
      >
        <span class="min-w-0 break-all">{{ node.label }}</span>
        <span
          v-if="node.value !== undefined"
          class="min-w-0 break-all font-semibold text-ink-gray-8"
          >{{ node.value }}</span
        >
      </span>
    </template>
    <template #item-suffix="{ node }">
      <FrappeBadge
        v-if="node.badge"
        :theme="node.badgeTheme as 'blue' | 'red'"
        variant="subtle"
        size="sm"
      >
        {{ node.badge }}
      </FrappeBadge>
    </template>
  </FrappeTree>
</template>
<script lang="ts">
import { t } from 'fyo';
import { Badge as FrappeBadge, Tree as FrappeTree } from 'frappe-ui';
import { PrintTemplateHint } from 'src/utils/printTemplates';
import { PropType, defineComponent } from 'vue';

type HintNode = {
  key: string;
  label: string;
  value?: string;
  badge?: string;
  badgeTheme?: 'blue' | 'red';
  expanded: boolean;
  children?: HintNode[];
};

function getKey(prefix: string, key: string, isArray: boolean): string {
  if (isArray) {
    return `${prefix}.${key}[number]`;
  }

  if (prefix.length) {
    return `${prefix}.${key}`;
  }

  return key;
}

function getNodes(
  hints: PrintTemplateHint,
  prefix: string,
  level: number
): HintNode[] {
  return Object.entries(hints)
    .map(([key, value]) => {
      const isArray = Array.isArray(value);
      const isGroup = typeof value === 'object' && value !== null;
      const label = getKey(prefix, key, isArray);

      if (!isGroup) {
        return { key: label, label, value: String(value), expanded: false };
      }

      const childHints = (
        isArray ? (value as PrintTemplateHint[])[0] : value
      ) as PrintTemplateHint | undefined;

      return {
        key: label,
        label,
        badge: isArray ? t`Array` : t`Object`,
        badgeTheme: isArray ? ('blue' as const) : ('red' as const),
        // Root level starts open, everything deeper starts collapsed.
        expanded: level === 0,
        children: childHints ? getNodes(childHints, label, level + 1) : [],
      };
    })
    .sort((a, b) => Number(!!a.children) - Number(!!b.children));
}

export default defineComponent({
  name: 'TemplateBuilderHint',
  components: { FrappeBadge, FrappeTree },
  props: {
    hints: {
      type: Object as PropType<PrintTemplateHint>,
      required: true,
    },
  },
  data() {
    return { nodes: [] as HintNode[] };
  },
  mounted() {
    this.nodes = getNodes(this.hints, '', 0);
  },
});
</script>
