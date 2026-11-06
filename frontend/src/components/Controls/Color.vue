<template>
  <ReadOnlyValue
    v-if="isReadOnly"
    :df="df"
    :value="value"
    :display-value="selectedColorLabel || undefined"
    :doc="doc"
    :border="border"
    :show-label="showLabel"
    :required="isRequired"
    :size="size"
    :container-styles="containerStyles"
    :error="error"
  >
    <template v-if="value" #trailing>
      <span
        class="ms-2 size-3 shrink-0 rounded-2"
        :style="{ backgroundColor: normalizedColor }"
        aria-hidden="true"
      />
    </template>
  </ReadOnlyValue>
  <div v-else>
    <FrappeFormLabel
      v-if="showLabel"
      size="md"
      class="mb-1.5"
      :label="df.label"
      :required="isRequired"
    />
    <Popover placement="bottom-end">
      <template #target>
        <FrappeButton
          :variant="frappeVariant"
          :size="frappeSize"
          :aria-label="df.label"
          :aria-invalid="error ? 'true' : undefined"
          class="w-full !justify-start text-base"
          :class="error ? '!border !border-outline-red-3' : ''"
        >
          <div class="flex items-center">
            <div
              v-if="value"
              class="size-3 rounded-2 me-1"
              :style="{ backgroundColor: normalizedColor }"
            ></div>
            <span v-if="value">
              {{ selectedColorLabel }}
            </span>
            <span v-else class="text-ink-gray-4">
              {{ inputPlaceholder }}
            </span>
          </div>
        </FrappeButton>
      </template>
      <template #content>
        <div class="w-48 p-3">
          <div class="grid grid-cols-5 gap-2">
            <FrappeButton
              v-for="color in colors"
              :key="color.value"
              variant="outline"
              size="sm"
              class="!size-7 !min-w-0 !p-0"
              :class="
                normalizedColor.toLowerCase() === color.value.toLowerCase()
                  ? 'ring-2 ring-outline-gray-5 ring-offset-2 ring-offset-[var(--surface-base)]'
                  : ''
              "
              :style="{ backgroundColor: color.value }"
              :tooltip="color.label"
              :aria-label="color.label"
              @click="setColorValue(color.value)"
            />
          </div>

          <div
            class="mt-3 flex items-center gap-2 rounded-4 border border-outline-gray-2 bg-surface-gray-1 p-1.5"
          >
            <input
              type="color"
              class="color-swatch size-7 flex-shrink-0 cursor-pointer"
              :value="normalizedColor"
              :title="t`Choose color`"
              :aria-label="t`Choose color`"
              @input="setColorFromEvent"
            />
            <FrappeTextInput
              class="min-w-0 flex-1 font-mono uppercase"
              :model-value="normalizedColor"
              :placeholder="t`Custom Hex`"
              :aria-label="t`Custom Hex`"
              @update:model-value="setColorValue"
            />
          </div>
        </div>
      </template>
    </Popover>
    <FrappeErrorMessage v-if="error" class="mt-1.5" :message="error" />
  </div>
</template>

<script>
import {
  Button as FrappeButton,
  ErrorMessage as FrappeErrorMessage,
  FormLabel as FrappeFormLabel,
  TextInput as FrappeTextInput,
} from 'frappe-ui';
import Popover from 'src/components/Popover.vue';
import Base from './Base.vue';
import ReadOnlyValue from './ReadOnlyValue.vue';

export default {
  name: 'Color',
  components: {
    Popover,
    ReadOnlyValue,
    FrappeButton,
    FrappeErrorMessage,
    FrappeFormLabel,
    FrappeTextInput,
  },
  extends: Base,
  computed: {
    colors() {
      if (Array.isArray(this.df.options) && this.df.options.length) {
        return this.df.options.filter(
          (color) => color && typeof color.value === 'string'
        );
      }

      return defaultColors;
    },
    normalizedColor() {
      if (typeof this.value !== 'string') {
        return '#000000';
      }

      const value = this.value.startsWith('#') ? this.value : `#${this.value}`;
      return isValidColor(value) ? value : '#000000';
    },
    selectedColorLabel() {
      const color = this.colors.find(
        (candidate) =>
          candidate.value.toLowerCase() === this.normalizedColor.toLowerCase()
      );
      return color ? color.label : this.value;
    },
  },
  methods: {
    setColorValue(value) {
      if (typeof value !== 'string') {
        return;
      }

      if (!value.startsWith('#')) {
        value = '#' + value;
      }

      if (isValidColor(value)) {
        this.triggerChange(value);
      }
    },
    setColorFromEvent(event) {
      if (!(event.target instanceof HTMLInputElement)) {
        return;
      }

      this.setColorValue(event.target.value);
    },
  },
};

const defaultColors = [
  { label: 'Red', value: '#f98080' },
  { label: 'Orange', value: '#fbbf70' },
  { label: 'Yellow', value: '#fde047' },
  { label: 'Green', value: '#86efac' },
  { label: 'Teal', value: '#5eead4' },
  { label: 'Blue', value: '#60a5fa' },
  { label: 'Indigo', value: '#818cf8' },
  { label: 'Purple', value: '#a78bfa' },
  { label: 'Pink', value: '#f472b6' },
  { label: 'Black', value: '#000000' },
];

function isValidColor(value) {
  return /^#[0-9A-F]{6}$/i.test(value);
}
</script>

<style scoped>
.color-swatch {
  appearance: none;
  border: 0;
  border-radius: 0.375rem;
  overflow: hidden;
  padding: 0;
}

.color-swatch::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-swatch::-webkit-color-swatch,
.color-swatch::-moz-color-swatch {
  border: 0;
}
</style>
