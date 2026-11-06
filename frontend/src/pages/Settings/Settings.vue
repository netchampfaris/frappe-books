<template>
  <FrappeSettingsDialog
    v-model:tab="activeTab"
    :open="isOpen"
    :shortcut="false"
    @update:open="onOpenChange"
  >
    <template #title>{{ t`Settings` }}</template>

    <FrappeSettingsSidebar>
      <FrappeSettingsNavGroup>
        <FrappeSettingsNavItem
          v-for="tab of tabOptions"
          :key="tab.value"
          :value="tab.value"
        >
          {{ tab.label }}
        </FrappeSettingsNavItem>
      </FrappeSettingsNavGroup>
    </FrappeSettingsSidebar>

    <FrappeSettingsContent>
      <FrappeSettingsPanel
        v-for="tab of tabOptions"
        :key="tab.value"
        :value="tab.value"
      >
        <FrappeSettingsHeader :title="tab.label">
          <template #actions>
            <FrappeButton
              v-if="canSave"
              variant="solid"
              theme="gray"
              :label="t`Save`"
              @click="sync"
            />
          </template>
        </FrappeSettingsHeader>

        <FrappeSettingsBody v-if="doc">
          <CommonFormSection
            v-for="([name, fields], idx) in sectionsFor(tab.value).entries()"
            :key="name + idx"
            ref="section"
            class="mt-6"
            :show-title="sectionsFor(tab.value).size > 1 && name !== t`Default`"
            :title="name"
            :fields="fields"
            :doc="doc"
            :errors="errors"
            @value-change="onValueChange"
          />
        </FrappeSettingsBody>
      </FrappeSettingsPanel>
    </FrappeSettingsContent>
  </FrappeSettingsDialog>
</template>
<script lang="ts">
import { DocValue } from 'fyo/core/types';
import { Doc } from 'fyo/model/doc';
import { ValidationError } from 'fyo/utils/errors';
import {
  Button as FrappeButton,
  SettingsBody as FrappeSettingsBody,
  SettingsContent as FrappeSettingsContent,
  SettingsDialog as FrappeSettingsDialog,
  SettingsHeader as FrappeSettingsHeader,
  SettingsNavGroup as FrappeSettingsNavGroup,
  SettingsNavItem as FrappeSettingsNavItem,
  SettingsPanel as FrappeSettingsPanel,
  SettingsSidebar as FrappeSettingsSidebar,
} from 'frappe-ui';
import { ModelNameEnum } from 'models/types';
import { Field, Schema } from 'schemas/types';
import { handleErrorWithDialog } from 'src/errorHandling';
import { getErrorMessage } from 'src/utils';
import { evaluateHidden } from 'src/utils/doc';
import { shortcutsKey } from 'src/utils/injectionKeys';
import { showDialog } from 'src/utils/interactive';
import { docsPathMap } from 'src/utils/misc';
import { docsPathRef } from 'src/utils/refs';
import { UIGroupedFields } from 'src/utils/types';
import { computed, defineComponent, inject } from 'vue';
import CommonFormSection from '../CommonForm/CommonFormSection.vue';

const COMPONENT_NAME = 'Settings';

export default defineComponent({
  components: {
    CommonFormSection,
    FrappeButton,
    FrappeSettingsBody,
    FrappeSettingsContent,
    FrappeSettingsDialog,
    FrappeSettingsHeader,
    FrappeSettingsNavGroup,
    FrappeSettingsNavItem,
    FrappeSettingsPanel,
    FrappeSettingsSidebar,
  },
  provide() {
    return { doc: computed(() => this.doc) };
  },
  setup() {
    return {
      shortcuts: inject(shortcutsKey),
    };
  },
  data() {
    return {
      errors: {},
      activeTab: ModelNameEnum.AccountingSettings,
      groupedFields: null,
      // Settings is a keep-alive route, so the dialog follows the route: it
      // opens when the page activates and closes when it deactivates. Without
      // this the teleported dialog would outlive the page it belongs to.
      isOpen: false,
      // Where dismissing the dialog goes. `router.back()` would do for a
      // sidebar click, but /settings can also be opened as the first route,
      // and then the previous history entry is outside the app.
      returnTo: '/',
    } as {
      errors: Record<string, string>;
      activeTab: string;
      groupedFields: null | UIGroupedFields;
      isOpen: boolean;
      returnTo: string;
    };
  },
  computed: {
    canSave() {
      return [
        ModelNameEnum.AccountingSettings,
        ModelNameEnum.InventorySettings,
        ModelNameEnum.Defaults,
        ModelNameEnum.POSSettings,
        ModelNameEnum.PrintSettings,
        ModelNameEnum.SystemSettings,
      ].some((s) => this.fyo.singles[s]?.canSave);
    },
    doc(): Doc | null {
      const doc = this.fyo.singles[this.activeTab];
      if (!doc) {
        return null;
      }

      return doc;
    },
    tabLabels(): Record<string, string> {
      return {
        [ModelNameEnum.AccountingSettings]: this.t`General`,
        [ModelNameEnum.PrintSettings]: this.t`Print`,
        [ModelNameEnum.InventorySettings]: this.t`Inventory`,
        [ModelNameEnum.Defaults]: this.t`Defaults`,
        [ModelNameEnum.POSSettings]: this.t`POS Settings`,
        [ModelNameEnum.SystemSettings]: this.t`System`,
      };
    },
    tabOptions(): { value: string; label: string }[] {
      return [...(this.groupedFields?.keys() ?? [])].map((value) => ({
        value,
        label: this.tabLabels[value] ?? value,
      }));
    },
    schemas(): Schema[] {
      const enableInventory = !!this.fyo.singles.AccountingSettings?.enableInventory;
      const enablePOS = !!this.fyo.singles.InventorySettings?.enablePointOfSale;
      return [
        ModelNameEnum.AccountingSettings,
        ModelNameEnum.InventorySettings,
        ModelNameEnum.Defaults,
        ModelNameEnum.POSSettings,
        ModelNameEnum.PrintSettings,
        ModelNameEnum.SystemSettings,
      ]
        .filter((s) => {
          if (s === ModelNameEnum.InventorySettings && !enableInventory) {
            return false;
          }

          if (s === ModelNameEnum.POSSettings && !enablePOS) {
            return false;
          }

          return true;
        })
        .map((s) => this.fyo.schemaMap[s]!);
    },
    activeGroup(): Map<string, Field[]> {
      if (!this.groupedFields) {
        return new Map();
      }

      const group = this.groupedFields.get(this.activeTab);
      if (!group) {
        throw new ValidationError(`Tab group ${this.activeTab} has no value set`);
      }

      return group;
    },
  },
  mounted() {
    if (this.fyo.store.isDevelopment) {
      // @ts-ignore
      window.settings = this;
    }

    this.update();
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      const settings = vm as unknown as { returnTo: string };
      settings.returnTo = from.name ? from.fullPath : '/';
    });
  },
  activated(): void {
    this.isOpen = true;
    const tab = this.$route.query.tab;
    if (typeof tab === 'string' && this.tabLabels[tab]) {
      this.activeTab = tab;
    }

    docsPathRef.value = docsPathMap.Settings ?? '';
    this.shortcuts?.pmod.set(COMPONENT_NAME, ['KeyS'], async () => {
      if (!this.canSave) {
        return;
      }

      await this.sync();
    });
  },
  async deactivated(): Promise<void> {
    this.isOpen = false;
    docsPathRef.value = '';
    this.shortcuts?.delete(COMPONENT_NAME);
    if (!this.canSave) {
      return;
    }
    await this.reset();
  },
  methods: {
    sectionsFor(schemaName: string): Map<string, Field[]> {
      return this.groupedFields?.get(schemaName) ?? new Map();
    },
    onOpenChange(open: boolean): void {
      if (open) {
        return;
      }

      // Dismissing the dialog leaves the settings route, which is what runs
      // `deactivated` and rolls back anything unsaved.
      void this.$router.push(this.returnTo);
    },
    async reset() {
      const resetableDocs = this.schemas
        .map(({ name }) => this.fyo.singles[name])
        .filter((doc) => doc?.dirty) as Doc[];

      for (const doc of resetableDocs) {
        await doc.load();
      }

      this.update();
    },
    async sync(): Promise<void> {
      const syncableDocs = this.schemas
        .map(({ name }) => this.fyo.singles[name])
        .filter((doc) => doc?.canSave) as Doc[];

      for (const doc of syncableDocs) {
        await this.syncDoc(doc);
      }

      this.update();
      await showDialog({
        title: this.t`Reload Frappe Books?`,
        detail: this.t`Changes made to settings will be visible on reload.`,
        type: 'info',
        buttons: [
          {
            label: this.t`Yes`,
            isPrimary: true,
            action: () => window.location.reload(),
          },
          {
            label: this.t`No`,
            action: () => null,
            isEscape: true,
          },
        ],
      });
    },
    async syncDoc(doc: Doc): Promise<void> {
      try {
        await doc.sync();
        this.updateGroupedFields();
      } catch (error) {
        await handleErrorWithDialog(error, doc);
      }
    },
    async onValueChange(field: Field, value: DocValue): Promise<void> {
      const { fieldname } = field;
      delete this.errors[fieldname];

      try {
        await this.doc?.set(fieldname, value ?? '');
      } catch (err) {
        if (!(err instanceof Error)) {
          return;
        }

        this.errors[fieldname] = getErrorMessage(err, this.doc ?? undefined);
      }

      this.update();
    },
    update(): void {
      this.updateGroupedFields();
    },
    updateGroupedFields(): void {
      const grouped: UIGroupedFields = new Map();
      const fields: Field[] = this.schemas.map((s) => s.fields).flat();

      for (const field of fields) {
        const schemaName = field.schemaName!;
        if (!grouped.has(schemaName)) {
          grouped.set(schemaName, new Map());
        }

        const tabbed = grouped.get(schemaName)!;
        const section = field.section ?? this.t`Miscellaneous`;
        if (!tabbed.has(section)) {
          tabbed.set(section, []);
        }

        if (field.meta) {
          continue;
        }

        const doc = this.fyo.singles[schemaName];
        if (evaluateHidden(field, doc)) {
          continue;
        }

        tabbed.get(section)!.push(field);
      }

      this.groupedFields = grouped;
    },
  },
});
</script>
