<template>
  <ReadOnlyValue
    v-if="isReadOnly"
    :df="df"
    :value="value"
    :doc="doc"
    :border="border"
    :show-label="showLabel"
    :required="isRequired"
    :size="size"
    :text-right="textRight"
    :container-styles="containerStyles"
    :error="error"
  />
  <FrappePassword
    v-else
    ref="input"
    spellcheck="false"
    :class="controlClasses"
    :model-value="inputValue"
    :label="showLabel ? df.label : undefined"
    :description="showLabel ? df.sub_label : undefined"
    :placeholder="inputPlaceholder"
    :required="isRequired"
    :error="error"
    :size="frappeSize"
    :variant="frappeVariant"
    :style="containerStyles"
    tabindex="0"
    @blur="onBlur"
    @focus="onFocus"
    @input="onInput"
  />
</template>

<script lang="ts">
import { Password as FrappePassword } from 'frappe-ui';
import { defineComponent } from 'vue';
import Base from './Base.vue';
import ReadOnlyValue from './ReadOnlyValue.vue';

export default defineComponent({
  name: 'Secret',
  components: { FrappePassword, ReadOnlyValue },
  extends: Base,
  emits: ['focus', 'input', 'change'],
  computed: {
    inputValue(): string {
      if (typeof this.value === 'string') {
        return this.value;
      }

      return this.value == null ? '' : String(this.value);
    },
  },
});
</script>
