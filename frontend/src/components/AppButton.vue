<template>
  <button
    :class="{ outline, disabled, rect, small, ...{ [color]: true }}"
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
    },
    color: {
      type: String,
      default: 'default'
    },
    small: {
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

  &.small {
    font-size: 12px;
    padding: 4px 12px;
  }

  &:hover {
    cursor: pointer;
    background-color: lighten($primary-color, 10%);
  }

  &.disabled {
    cursor: not-allowed;
    background-color: #aaa;
  }

  &.blue {
    &:hover {
      background-color: lighten($blue-color, 10%);
    }
  }

  &.red {
    &:hover {
      background-color: lighten($red-color, 10%);
    }
  }

  &.gray {
    &:hover {
      background-color: lighten($gray-color, 10%);
    }
  }

  &.dark-green {
    background-color: $dark-green-color;

    &:hover {
      background-color: lighten($dark-green-color, 10%);
    }
  }

  &.white {
    background-color: white;
    color: $dark-green-color;

    &:hover {
      background-color: darken(white, 10%);
    }
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

  &.blue {
    border: 1px solid $blue-color;

    &:hover {
      background-color: $blue-color;
    }
  }

  &.red {
    border: 1px solid $red-color;

    &:hover {
      background-color: $red-color;
    }
  }

  &.gray {
    border: 1px solid $gray-color;

    &:hover {
      background-color: $gray-color;
    }
  }
}

.rect {
  border-radius: 4px;
  box-shadow: none;
  height: 100%;
  font-size: 16px;
}
</style>
