<template>
  <div class="flex flex-col h-full">
    <SectionHeader>
      <template #title>{{ t`Top Expenses` }}</template>
    </SectionHeader>

    <div v-if="hasData" class="h-64 w-full">
      <FrappeDonutChart
        :data="expenses"
        category="account"
        value="total"
        :center-label="t`Total Spending`"
        :format="(value: number) => fyo.format(value, 'Currency')"
        :palette="expensePalette"
      />
    </div>

    <!-- Empty Message -->
    <div v-if="expenses.length === 0" class="flex-1 w-full h-full flex-center my-20">
      <span class="text-base text-ink-gray-6">
        {{ t`No expenses in this period` }}
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import { useColorScheme } from 'frappe-ui';
import { DonutChart as FrappeDonutChart } from 'frappe-ui/charts';
import { fyo } from 'src/initFyo';
import { uicolors } from 'src/utils/colors';
import { getDatesAndPeriodList } from 'src/utils/misc';
import { defineComponent } from 'vue';
import DashboardChartBase from './BaseDashboardChart.vue';
import SectionHeader from './SectionHeader.vue';

// Linting broken in this file cause of `extends: ...`
/*
  eslint-disable @typescript-eslint/no-unsafe-argument,
  @typescript-eslint/no-unsafe-return,
  @typescript-eslint/restrict-plus-operands
*/
export default defineComponent({
  name: 'Expenses',
  components: {
    FrappeDonutChart,
    SectionHeader,
  },
  extends: DashboardChartBase,
  setup() {
    const { colorScheme } = useColorScheme();
    return { colorScheme };
  },
  data: () => ({
    expenses: [] as {
      account: string;
      total: number;
      color: { color: string; darkColor: string };
    }[],
  }),
  computed: {
    isDarkMode(): boolean {
      return this.colorScheme === 'dark';
    },
    totalExpense(): number {
      return this.expenses.reduce((sum, expense) => sum + expense.total, 0);
    },
    hasData(): boolean {
      return this.expenses.length > 0;
    },
    expensePalette(): string[] {
      return this.expenses.map(({ color }) => (this.isDarkMode ? color.darkColor : color.color));
    },
  },
  activated() {
    this.setData();
  },
  methods: {
    async setData() {
      const { fromDate, toDate } = getDatesAndPeriodList(this.period);
      let topExpenses = await fyo.db.getTopExpenses(fromDate.toISO(), toDate.toISO());
      const shades = [
        uicolors.pink['500'],
        uicolors.pink['400'],
        uicolors.pink['300'],
        uicolors.pink['200'],
        uicolors.pink['100'],
      ];

      const darkshades = [
        uicolors.pink['600'],
        uicolors.pink['500'],
        uicolors.pink['400'],
        uicolors.pink['300'],
        uicolors.pink['200'] + 'CC',
      ];

      this.expenses = topExpenses
        .filter((e) => e.total > 0)
        .map((d, i) => {
          return {
            account: d.account,
            total: d.total,
            color: { color: shades[i], darkColor: darkshades[i] },
          };
        });
    },
  },
});
</script>
