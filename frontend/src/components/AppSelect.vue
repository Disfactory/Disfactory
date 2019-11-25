<template>
  <div class="select">
    <select
      v-bind="$attrs"
      v-model="inputValue"
    >
      <option
        v-for="option in items"
        :key="option.value"
        :value="option.value"
      >
        {{ option.text }}
      </option>
    </select>
  </div>
</template>

<script lang="ts">
import { createComponent, PropType, computed } from '@vue/composition-api'

export default createComponent({
  name: 'AppSelect',
  props: {
    value: {
      type: null,
      required: true
    },
    items: {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      type: Array as PropType<{ text: string; value: any }[]>,
      required: true
    }
  },
  setup (props, context) {
    const inputValue = computed({
      get: () => props.value,
      set: (value) => context.emit('input', value)
    })

    return {
      inputValue
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
.select {
  position: relative;
  width: 100%;

  select {
    width: 100%;
    outline: none;
    padding: 10px 15px;
    border: 1px solid $second-color;
    border-radius: 4px;
    color: $font-color;
    color: rgba($font-color, 0);
    background-color: #fff;
    text-shadow: 0 0 0 $font-color;
    font-size: $form-font-size;
    appearance: none;

    > option:not(:checked),
      option:not(:hover),
      option:not(:focus) {
      color: $font-color;
    }

    &:focus, &:hover {
      outline: none;
    }
  }

  &:before {
    position: absolute;
    top: calc(50% + 5px);
    right: 15px;
    border: solid transparent;
    border-width: 10px;
    border-top-color: $second-color;
    content: '';
    transform: translateY(-50%);
    pointer-events: none;
  }
}
</style>
