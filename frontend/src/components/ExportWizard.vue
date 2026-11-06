<template>
  <div>
    <!-- Export Config -->
    <div class="flex flex-wrap items-end gap-4 pb-4">
      <Check
        v-if="configFields.useListFilters && Object.keys(listFilters).length"
        class="min-h-8 w-56"
        :df="configFields.useListFilters"
        :space-between="true"
        :show-label="true"
        :label-right="false"
        :value="useListFilters"
        :border="true"
        @change="(value: boolean) => (useListFilters = value)"
      />
      <Select
        v-if="configFields.exportFormat"
        class="w-56"
        :df="configFields.exportFormat"
        :value="exportFormat"
        :border="true"
        :show-label="true"
        @change="(value: ExportFormat) => (exportFormat = value)"
      />
      <Int
        v-if="configFields.limit"
        class="w-56"
        :df="configFields.limit"
        :value="limit ?? undefined"
        :border="true"
        :show-label="true"
        :text-right="false"
        @change="(value: number) => (limit = value)"
      />
    </div>
    <FrappeDivider />

    <!-- Fields Selection -->
    <FrappeScrollArea class="max-h-80">
      <!-- Main Fields -->
      <div class="py-4">
        <h2 class="text-sm font-semibold text-ink-gray-8">
          {{ fyo.schemaMap[schemaName]?.label ?? schemaName }}
        </h2>
        <div
          class="
            mt-2
            grid grid-cols-3
            gap-x-6 gap-y-2
            rounded-2
            border
            p-3
            border-outline-gray-1
          "
        >
          <Check
            v-for="ef of fields"
            :key="ef.fieldname"
            class="min-w-0"
            :label-class="
              ef.fieldtype === 'Table'
                ? 'text-sm text-ink-gray-6 font-semibold'
                : 'text-sm text-ink-gray-6'
            "
            :df="getField(ef)"
            :show-label="true"
            :value="ef.export"
            @change="(value: boolean) => setExportFieldValue(ef, value)"
          />
        </div>
      </div>

      <!-- Table Fields -->
      <div v-for="efs of filteredTableFields" :key="efs.fieldname" class="py-4">
        <h2 class="text-sm font-semibold text-ink-gray-8">
          {{ fyo.schemaMap[efs.target]?.label ?? schemaName }}
        </h2>
        <div
          class="
            mt-2
            grid grid-cols-3
            gap-x-6 gap-y-2
            rounded-2
            border
            p-3
            border-outline-gray-1
          "
        >
          <Check
            v-for="ef of efs.fields"
            :key="ef.fieldname"
            class="min-w-0"
            label-class="text-ink-gray-6"
            :df="getField(ef)"
            :show-label="true"
            :value="ef.export"
            @change="(value: boolean) => setExportFieldValue(ef, value, efs.target)"
          />
        </div>
      </div>
    </FrappeScrollArea>

    <!-- Export Button -->
    <FrappeDivider />
    <div class="pt-4 flex justify-between items-center">
      <p class="text-sm text-ink-gray-6">
        {{ t`${numSelected} fields selected` }}
      </p>
      <FrappeButton
        variant="solid"
        theme="gray"
        :label="t`Export`"
        @click="exportData"
      />
    </div>
  </div>
</template>
<script lang="ts">
import { t } from 'fyo';
import { Field, FieldTypeEnum } from 'schemas/types';
import { fyo } from 'src/initFyo';
import { saveExportData } from 'reports/commonExporter';
import {
  getCsvExportData,
  getExportFields,
  getExportTableFields,
  getJsonExportData,
} from 'src/utils/export';
import { ExportField, ExportFormat, ExportTableField } from 'src/utils/types';
import { QueryFilter } from 'utils/db/types';
import {
  Button as FrappeButton,
  Divider as FrappeDivider,
  ScrollArea as FrappeScrollArea,
} from 'frappe-ui';
import { PropType, defineComponent } from 'vue';
import Check from './Controls/Check.vue';
import Int from './Controls/Int.vue';
import Select from './Controls/Select.vue';

interface ExportWizardData {
  useListFilters: boolean;
  exportFormat: ExportFormat;
  fields: ExportField[];
  limit: number | null;
  tableFields: ExportTableField[];
  numUnfilteredEntries: number;
}

export default defineComponent({
  components: {
    Check,
    FrappeButton,
    FrappeDivider,
    FrappeScrollArea,
    Int,
    Select,
  },
  props: {
    schemaName: { type: String, required: true },
    listFilters: { type: Object as PropType<QueryFilter>, default: () => {} },
  },
  data() {
    const fields = fyo.schemaMap[this.schemaName]?.fields ?? [];
    const exportFields = getExportFields(fields);
    const exportTableFields = getExportTableFields(fields, fyo);

    return {
      limit: null,
      useListFilters: true,
      exportFormat: 'csv',
      fields: exportFields,
      tableFields: exportTableFields,
    } as ExportWizardData;
  },
  computed: {
    filteredTableFields() {
      return this.tableFields.filter((f) => {
        const ef = this.getExportField(f.fieldname);
        return !!ef?.export;
      });
    },
    numSelected() {
      return (
        this.filteredTableFields.reduce(
          (acc, f) => f.fields.filter((f) => f.export).length + acc,
          0
        ) +
        this.fields.filter(
          (f) => f.fieldtype !== FieldTypeEnum.Table && f.export
        ).length
      );
    },
    configFields() {
      return {
        useListFilters: {
          fieldtype: 'Check',
          label: t`Use List Filters`,
          fieldname: 'useListFilters',
        } as Field,
        limit: {
          placeholder: t`No limit`,
          fieldtype: 'Int',
          label: t`Limit number of rows`,
          fieldname: 'limit',
        } as Field,
        exportFormat: {
          fieldtype: 'Select',
          label: t`Export Format`,
          fieldname: 'exportFormat',
          options: [
            { value: 'json', label: 'JSON' },
            { value: 'csv', label: 'CSV' },
          ],
        } as Field,
      };
    },
  },
  methods: {
    getField(ef: ExportField): Field {
      return {
        fieldtype: 'Check',
        label: ef.label,
        fieldname: ef.fieldname,
      };
    },
    getExportField(
      fieldname: string,
      target?: string
    ): ExportField | undefined {
      let fields: ExportField[] | undefined;

      if (!target) {
        fields = this.fields;
      } else {
        fields = this.tableFields.find((f) => f.target === target)?.fields;
      }

      if (!fields) {
        return undefined;
      }

      return fields.find((f) => f.fieldname === fieldname);
    },
    setExportFieldValue(ef: ExportField, value: boolean, target?: string) {
      const field = this.getExportField(ef.fieldname, target);
      if (!field) {
        return;
      }

      field.export = value;
    },
    async exportData() {
      const filters = JSON.parse(
        JSON.stringify(this.useListFilters ? this.listFilters : {})
      );

      let data: string;
      if (this.exportFormat === 'json') {
        data = await getJsonExportData(
          this.schemaName,
          this.fields,
          this.tableFields,
          this.limit,
          filters,
          fyo
        );
      } else {
        data = await getCsvExportData(
          this.schemaName,
          this.fields,
          this.tableFields,
          this.limit,
          filters,
          fyo
        );
      }

      await this.saveExportData(data);
    },
    async saveExportData(data: string) {
      const fileName = this.getFileName();
      saveExportData(
        data,
        `${fileName}.${this.exportFormat}`,
        fyo.t`Export Successful`
      );
    },
    getFileName() {
      const label = fyo.schemaMap[this.schemaName]?.label ?? this.schemaName;
      const fileName = label.toLowerCase().replace(/\s/g, '-');
      const dateString = new Date().toISOString().split('T')[0];
      return `${fileName}_${dateString}`;
    },
  },
});
</script>
