<template>
  <input
    v-bind="$attrs"
    v-model="inputValue"
    :type="type"
  >
</template>

<script>
import { computed, createComponent } from '@vue/composition-api'
export default createComponent({
  name: 'AppTextField',
  props: {
    type: {
      type: String,
      default: 'text'
    },
    value: {
      type: String,
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
input {
  border: 1px solid $second-color;
  border-radius: 4px;
  padding: 10px 15px;
  outline: none;

  font-size: $form-font-size;

  &::placeholder {
    color: rgb(186, 186, 186);
  }
}
</style>
