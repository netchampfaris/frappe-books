<template>
  <FrappeSidebar
    :disable-collapse="true"
    width="var(--w-sidebar)"
    class="py-2 h-full min-h-0 flex flex-col overflow-hidden bg-surface-sidebar"
    :class="{
      'window-drag': platform !== 'Windows',
    }"
  >
    <FrappeScrollArea class="min-h-0 flex-1">
      <!-- Company name -->
      <div
        class="px-4 flex flex-row items-center justify-between mb-4"
        :class="
          platform === 'Mac' && languageDirection === 'ltr' ? 'mt-10' : 'mt-2'
        "
      >
        <h6
          data-testid="company-name"
          class="font-semibold text-ink-gray-8 whitespace-nowrap overflow-auto no-scrollbar select-none"
        >
          {{ companyName }}
        </h6>

        <!-- History Navigation -->
        <div class="window-no-drag shrink-0 flex items-center gap-0.5">
          <FrappeButton
            variant="ghost"
            size="xs"
            icon="lucide-chevron-left"
            :disabled="!historyState.back"
            :tooltip="t`Back`"
            :aria-label="t`Back`"
            @click="$router.back()"
          />
          <FrappeButton
            variant="ghost"
            size="xs"
            icon="lucide-chevron-right"
            :disabled="!historyState.forward"
            :tooltip="t`Forward`"
            :aria-label="t`Forward`"
            @click="$router.forward()"
          />
        </div>
      </div>

      <!-- Search -->
      <SearchBar>
        <template #trigger="{ open }">
          <FrappeSidebarItem
            :label="t`Search`"
            class="mx-2 mb-0.5"
            @click="open"
          >
            <template #prefix>
              <NavIcon name="search" />
            </template>
            <template #suffix>
              <FrappeKeyboardShortcut combo="Mod+K" class="mr-2" />
            </template>
          </FrappeSidebarItem>
        </template>
      </SearchBar>

      <!-- Sidebar Items -->
      <div v-for="group in groups" :key="group.label">
        <FrappeSidebarItem
          :label="group.label"
          :active="Boolean(isGroupActive(group) && !group.items)"
          class="mx-2 mb-0.5 [&_[data-slot='sidebar-item-suffix']]:hidden"
          @click="routeToSidebarItem(group)"
        >
          <template #prefix>
            <NavIcon :name="group.icon" :active="!!isGroupActive(group)" />
          </template>
        </FrappeSidebarItem>

        <!-- Expanded Group -->
        <div v-if="group.items && isGroupActive(group)">
          <FrappeSidebarItem
            v-for="item in group.items"
            :key="item.label"
            :label="item.label"
            :active="Boolean(isItemActive(item))"
            class="mx-2 mb-0.5"
            @click="routeToSidebarItem(item)"
          >
            <!--
              Align the sub-item label with its parent's. SidebarItem lays its
              row out as pl-2 (8px) + prefix + label ml-2 (8px), so a parent
              label starts at 8 + 18 (NavIcon's default 18px glyph) + 8 = 34px.
              Substituting a spacer exactly one icon wide keeps the sub-item on
              the same 34px, which the old `ps-7` (28) + `w-0` prefix missed by
              2px (28 + 8 + 0 + 8 = 36).
            -->
            <template #prefix><span class="w-[18px]" /></template>
          </FrappeSidebarItem>
        </div>
      </div>
    </FrappeScrollArea>

    <!-- Report Issue and DB Switcher -->
    <div class="window-no-drag flex-shrink-0 flex flex-col gap-0.5 py-2 px-4">
      <FrappeSidebarItem :label="t`Help`" @click="openDocumentation">
        <template #prefix>
          <NavIcon name="help-circle" :size="16" />
        </template>
      </FrappeSidebarItem>

      <FrappeSidebarItem :label="t`Shortcuts`" @click="viewShortcuts = true">
        <template #prefix>
          <NavIcon name="command" :size="16" />
        </template>
      </FrappeSidebarItem>

      <FrappeSidebarItem
        v-if="platform !== 'Web'"
        data-testid="change-db"
        :label="t`Change DB`"
        @click="$emit('change-db-file')"
      >
        <template #prefix>
          <NavIcon name="database" :size="16" />
        </template>
      </FrappeSidebarItem>

      <div class="flex items-center gap-2">
        <FrappeSidebarItem
          :label="t`Report Issue`"
          class="min-w-0 flex-1"
          @click="() => reportIssue()"
        >
          <template #prefix>
            <NavIcon name="flag" :size="16" />
          </template>
        </FrappeSidebarItem>

        <FrappeButton
          variant="ghost"
          icon="lucide-panel-left-close"
          :tooltip="t`Hide sidebar`"
          :aria-label="t`Hide sidebar`"
          class="shrink-0 rtl-rotate-180"
          @click="() => toggleSidebar()"
        />
      </div>
    </div>

    <FrappeDialog
      v-model:open="viewShortcuts"
      size="2xl"
      :title="t`Shortcuts`"
    >
      <ShortcutsHelper class="w-full" />
    </FrappeDialog>
  </FrappeSidebar>
</template>
<script lang="ts">
import {
  Button as FrappeButton,
  Dialog as FrappeDialog,
  KeyboardShortcut as FrappeKeyboardShortcut,
  ScrollArea as FrappeScrollArea,
  Sidebar as FrappeSidebar,
  SidebarItem as FrappeSidebarItem,
} from 'frappe-ui';
import { reportIssue } from 'src/errorHandling';
import { fyo } from 'src/initFyo';
import { languageDirectionKey, shortcutsKey } from 'src/utils/injectionKeys';
import { docsPathRef, historyState } from 'src/utils/refs';
import { getSidebarConfig } from 'src/utils/sidebarConfig';
import {
  getSidebarPath,
  matchesSidebarPath,
} from 'src/utils/sidebarNavigation';
import { SidebarConfig, SidebarItem, SidebarRoot } from 'src/utils/types';
import { routeTo, toggleSidebar } from 'src/utils/ui';
import { defineComponent, inject } from 'vue';
import router from '../router';
import NavIcon from './NavIcon.vue';
import SearchBar from './SearchBar.vue';
import ShortcutsHelper from './ShortcutsHelper.vue';

const COMPONENT_NAME = 'Sidebar';

export default defineComponent({
  components: {
    FrappeButton,
    FrappeDialog,
    FrappeKeyboardShortcut,
    FrappeScrollArea,
    FrappeSidebar,
    FrappeSidebarItem,
    NavIcon,
    SearchBar,
    ShortcutsHelper,
  },
  emits: ['change-db-file'],
  setup() {
    return {
      historyState,
      languageDirection: inject(languageDirectionKey),
      shortcuts: inject(shortcutsKey),
    };
  },
  data() {
    return {
      companyName: '',
      groups: [],
      viewShortcuts: false,
      activeGroup: null,
    } as {
      companyName: string;
      groups: SidebarConfig;
      viewShortcuts: boolean;
      activeGroup: null | SidebarRoot;
    };
  },
  async mounted() {
    // Registered before the awaits below so the shortcuts do not hinge on the
    // company/config load. The sidebar is never keep-alive'd, so Back binds
    // here and unbinds in beforeUnmount, not in activated/deactivated as it
    // did while it lived in the page header.
    this.shortcuts?.shift.set(COMPONENT_NAME, ['KeyH'], () => {
      if (document.body === document.activeElement) {
        this.toggleSidebar();
      }
    });
    this.shortcuts?.set(COMPONENT_NAME, ['F1'], () => this.openDocumentation());
    this.shortcuts?.shift.set(COMPONENT_NAME, ['Backspace'], () => {
      if (historyState.back) {
        this.$router.back();
      }
    });

    const { companyName } = await fyo.doc.getDoc('AccountingSettings');
    this.companyName = companyName as string;
    this.groups = await getSidebarConfig();

    this.setActiveGroup();
    router.afterEach(() => {
      this.setActiveGroup();
    });
  },
  beforeUnmount() {
    this.shortcuts?.delete(COMPONENT_NAME);
  },
  methods: {
    routeTo,
    reportIssue,
    toggleSidebar,
    openDocumentation() {
      window.open(
        'https://docs.frappe.io/' + docsPathRef.value,
        '_blank',
        'noopener,noreferrer'
      );
    },
    setActiveGroup() {
      const { path } = this.$route;
      const fallBackGroup = this.activeGroup;
      this.activeGroup =
        this.groups.find((g) => {
          if (path.startsWith(g.route + '/') && g.route !== '/') {
            return true;
          }

          if (g.route === path) {
            return true;
          }

          if (g.items) {
            let activeItem = g.items.filter(
              ({ route }) =>
                route === decodeURI(path) || path.startsWith(route + '/')
            );

            if (activeItem.length) {
              return true;
            }
          }
        }) ??
        (fallBackGroup?.items?.some(this.isItemActive)
          ? fallBackGroup
          : this.groups.find((group) =>
              group.items?.some(this.isItemActive)
            )) ??
        fallBackGroup ??
        this.groups[0];
    },
    isItemActive(item: SidebarItem) {
      return matchesSidebarPath(getSidebarPath(this.$route), item.route);
    },
    isGroupActive(group: SidebarRoot) {
      return this.activeGroup && group.label === this.activeGroup.label;
    },
    routeToSidebarItem(item: SidebarItem | SidebarRoot) {
      routeTo(this.getPath(item));
    },
    getPath(item: SidebarItem | SidebarRoot) {
      const { route: path, filters } = item;
      if (!filters) {
        return path;
      }

      return { path, query: { filters: JSON.stringify(filters) } };
    },
  },
});
</script>
