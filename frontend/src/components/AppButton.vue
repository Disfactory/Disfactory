<template>
  <button
    :class="{ outline, disabled, rect }"
    @click="click"
  >
    <slot />
  </button>
</template>

<script>
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'AppButton',
  props: {
    outline: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    rect: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const click = () => {
      if (!props.disabled) {
        context.emit('click')
      }
    }

    return {
      click
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
button {
  width: 100%;
  background-color: $primary-color;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
  border: 1px solid #fff;
  border-radius: 24px;
  padding: 10px 21px;
  user-select: none;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  color: $dark-font-color;
  font-size: 20px;
  text-align: center;

  &:hover {
    cursor: pointer;
    background-color: #87a400;
  }

  &.disabled {
    cursor: not-allowed;
    background-color: #aaa;
  }
}

.outline {
  border: 1px solid $primary-color;
  background-color: #fff;
  color: $font-color;

  &:hover {
    cursor: pointer;
    background-color: $primary-color;
    color: $dark-font-color;
  }
}

.rect {
  border-radius: 4px;
  box-shadow: none;
  height: 100%;
}
</style>
